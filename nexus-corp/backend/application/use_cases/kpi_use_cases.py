from typing import List

from core.logging_config import get_logger
from domain.entities.kpi import KPI
from domain.repositories.kpi_repository import KPIRepository
from domain.repositories.knowledge_rule_repository import KnowledgeRuleRepository
from domain.repositories.scenario_repository import ScenarioRepository
from domain.repositories.decision_repository import DecisionRepository
from domain.repositories.recommendation_repository import RecommendationRepository
from domain.repositories.feedback_repository import FeedbackRepository

logger = get_logger(__name__)

MONTH_NAMES = [
    "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]


class ListKPIsUseCase:

    def __init__(self, kpi_repo: KPIRepository):
        self.kpi_repo = kpi_repo

    def execute(self, skip: int = 0, limit: int = 100) -> List[KPI]:
        return self.kpi_repo.list_all(skip=skip, limit=limit)


class GetDashboardUseCase:

    def __init__(
        self,
        kpi_repo: KPIRepository,
        rule_repo: KnowledgeRuleRepository,
        scenario_repo: ScenarioRepository,
        decision_repo: DecisionRepository,
        recommendation_repo: RecommendationRepository,
        feedback_repo: FeedbackRepository,
    ):
        self.kpi_repo = kpi_repo
        self.rule_repo = rule_repo
        self.scenario_repo = scenario_repo
        self.decision_repo = decision_repo
        self.recommendation_repo = recommendation_repo
        self.feedback_repo = feedback_repo

    def execute(self) -> dict:
        total_rules = self.rule_repo.count()
        total_scenarios = self.scenario_repo.count()
        total_decisions = self.decision_repo.count()
        accepted_recommendations = self.recommendation_repo.count_accepted()
        rejected_recommendations = self.recommendation_repo.count_rejected()
        avg_satisfaction = self.feedback_repo.get_average_rating()

        # Decisions by month chart data
        raw_by_month = self.decision_repo.count_by_month()
        decisions_by_month = [
            {
                "label": f"{MONTH_NAMES[r['month']]} {r['year']}",
                "count": r["count"],
                "month": r["month"],
                "year": r["year"],
            }
            for r in raw_by_month
        ]

        # Rules by category chart data
        rules_by_category = self.rule_repo.count_by_category() if hasattr(self.rule_repo, 'count_by_category') else []

        # Feedback distribution chart data
        feedback_distribution = self.feedback_repo.get_rating_distribution()

        return {
            "total_rules": total_rules,
            "total_scenarios": total_scenarios,
            "total_decisions": total_decisions,
            "accepted_recommendations": accepted_recommendations,
            "rejected_recommendations": rejected_recommendations,
            "avg_satisfaction": avg_satisfaction,
            "decisions_by_month": decisions_by_month,
            "rules_by_category": rules_by_category,
            "feedback_distribution": feedback_distribution,
        }
