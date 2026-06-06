import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status

from core.logging_config import get_logger
from domain.entities.decision import Decision
from domain.entities.recommendation import Recommendation
from domain.entities.scenario import Scenario
from domain.entities.audit_log import AuditLog
from domain.repositories.decision_repository import DecisionRepository
from domain.repositories.recommendation_repository import RecommendationRepository
from domain.repositories.scenario_repository import ScenarioRepository
from domain.repositories.audit_repository import AuditRepository
from application.services.rule_engine import RuleEngine

logger = get_logger(__name__)

VALID_STATUSES = {"pendiente", "aceptada", "rechazada"}


class ListDecisionsUseCase:

    def __init__(self, decision_repo: DecisionRepository):
        self.decision_repo = decision_repo

    def execute(self, skip: int = 0, limit: int = 100) -> List[Decision]:
        return self.decision_repo.list_all(skip=skip, limit=limit)


class GetDecisionUseCase:

    def __init__(
        self,
        decision_repo: DecisionRepository,
        recommendation_repo: RecommendationRepository,
    ):
        self.decision_repo = decision_repo
        self.recommendation_repo = recommendation_repo

    def execute(self, decision_id: uuid.UUID) -> dict:
        decision = self.decision_repo.get_by_id(decision_id)
        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Decision {decision_id} no encontrada",
            )
        recommendations = self.recommendation_repo.get_by_decision_id(decision_id)
        return {"decision": decision, "recommendations": recommendations}


class AnalyzeDecisionUseCase:
    """
    Core use case: runs what-if analysis on a scenario.
    Fires the rule engine, saves Decision + Recommendations.
    """

    def __init__(
        self,
        rule_engine: RuleEngine,
        decision_repo: DecisionRepository,
        recommendation_repo: RecommendationRepository,
        scenario_repo: ScenarioRepository,
        audit_repo: AuditRepository,
    ):
        self.rule_engine = rule_engine
        self.decision_repo = decision_repo
        self.recommendation_repo = recommendation_repo
        self.scenario_repo = scenario_repo
        self.audit_repo = audit_repo

    def execute(
        self,
        scenario_id: Optional[uuid.UUID],
        stock_level: int,
        demand_level: str,
        risk_level: str,
        notes: Optional[str],
        created_by: uuid.UUID,
        ip_address: Optional[str] = None,
        scenario_name: Optional[str] = None,
        scenario_description: Optional[str] = None,
    ) -> dict:
        # If no scenario_id provided, auto-create one from params
        if scenario_id is None:
            new_scenario = Scenario(
                id=uuid.uuid4(),
                name=scenario_name or f"What-If {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                description=scenario_description or "",
                stock_level=stock_level,
                demand_level=demand_level,
                risk_level=risk_level,
                created_by=created_by,
                created_at=datetime.utcnow(),
            )
            saved_scenario = self.scenario_repo.create(new_scenario)
            scenario_id = saved_scenario.id
        else:
            # Validate scenario exists
            scenario = self.scenario_repo.get_by_id(scenario_id)
            if not scenario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Escenario {scenario_id} no encontrado",
                )

        # Build scenario dict for rule engine
        scenario_data = {
            "stock_level": stock_level,
            "demand_level": demand_level,
            "risk_level": risk_level,
        }

        # Run rule engine
        rule_results = self.rule_engine.evaluate(scenario_data)

        if not rule_results:
            logger.info(f"No rules fired for scenario {scenario_id}")

        now = datetime.utcnow()

        # Build recommendation summaries for Decision.recommendations JSON
        rec_summaries = [
            {
                "rule_id": str(r.rule_id),
                "rule_name": r.rule_name,
                "action": r.action,
                "priority": r.priority,
            }
            for r in rule_results
        ]

        # Create decision record
        decision = Decision(
            id=uuid.uuid4(),
            scenario_id=scenario_id,
            recommendations=rec_summaries,
            rules_fired=[r.rule_id for r in rule_results],
            status="pendiente",
            notes=notes,
            created_by=created_by,
            created_at=now,
        )
        saved_decision = self.decision_repo.create(decision)

        # Create individual recommendation records
        recommendation_entities = [
            Recommendation(
                id=uuid.uuid4(),
                decision_id=saved_decision.id,
                rule_id=r.rule_id,
                text=r.action,
                priority=r.priority,
                justification=r.justification,
                is_accepted=False,
            )
            for r in rule_results
        ]

        saved_recommendations = []
        if recommendation_entities:
            saved_recommendations = self.recommendation_repo.create_many(recommendation_entities)

        # Audit log
        self.audit_repo.create(AuditLog(
            id=uuid.uuid4(),
            user_id=created_by,
            action="CREATE",
            entity_type="Decision",
            entity_id=saved_decision.id,
            details={
                "scenario_id": str(scenario_id),
                "rules_fired_count": len(rule_results),
                "stock_level": stock_level,
                "demand_level": demand_level,
                "risk_level": risk_level,
            },
            ip_address=ip_address,
            created_at=now,
        ))

        logger.info(
            f"Decision {saved_decision.id} created with {len(rule_results)} recommendations "
            f"for scenario {scenario_id}"
        )

        return {"decision": saved_decision, "recommendations": saved_recommendations}


class UpdateDecisionStatusUseCase:

    def __init__(
        self,
        decision_repo: DecisionRepository,
        audit_repo: AuditRepository,
    ):
        self.decision_repo = decision_repo
        self.audit_repo = audit_repo

    def execute(
        self,
        decision_id: uuid.UUID,
        new_status: str,
        notes: Optional[str],
        updated_by: uuid.UUID,
        ip_address: Optional[str] = None,
    ) -> Decision:
        if new_status not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Status debe ser uno de: {', '.join(VALID_STATUSES)}",
            )

        decision = self.decision_repo.get_by_id(decision_id)
        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Decision {decision_id} no encontrada",
            )

        old_status = decision.status
        decision.status = new_status
        if notes is not None:
            decision.notes = notes

        updated = self.decision_repo.update(decision)

        self.audit_repo.create(AuditLog(
            id=uuid.uuid4(),
            user_id=updated_by,
            action="UPDATE",
            entity_type="Decision",
            entity_id=decision_id,
            details={"old_status": old_status, "new_status": new_status},
            ip_address=ip_address,
            created_at=datetime.utcnow(),
        ))

        logger.info(f"Decision {decision_id} status changed from '{old_status}' to '{new_status}'")
        return updated
