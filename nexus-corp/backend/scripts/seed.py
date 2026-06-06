"""
Nexus-Corp KBDSS - Database Seed Script
========================================
Populates the database with initial data:
- 4 Roles
- 4 Users (one per role)
- 6 Knowledge Rules
- 3 Scenarios
- 2 Decisions with Recommendations
- 5 KPIs
- 2 Feedback entries

Run from the backend directory:
    python scripts/seed.py
"""

import sys
import os
import uuid
from datetime import datetime

# Add backend root to Python path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from infrastructure.database.connection import SessionLocal, create_tables
from infrastructure.database.models import (
    RoleModel,
    UserModel,
    KnowledgeRuleModel,
    ScenarioModel,
    DecisionModel,
    RecommendationModel,
    FeedbackModel,
    KPIModel,
    AuditLogModel,
)
from infrastructure.security.password_handler import hash_password
from core.logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger("seed")


def seed_roles(db) -> dict:
    """Seed roles and return {name: RoleModel} dict."""
    logger.info("Seeding roles...")

    roles_data = [
        {
            "id": uuid.uuid4(),
            "name": "admin_sistema",
            "description": "Administrador del sistema con acceso total a usuarios, roles y auditoría",
            "permissions": [
                "users:read", "users:write", "users:delete",
                "roles:read",
                "audit:read",
                "rules:read", "rules:write", "rules:delete",
                "scenarios:read", "scenarios:write", "scenarios:delete",
                "decisions:read", "decisions:write",
                "feedback:read", "feedback:write",
                "kpis:read",
            ],
        },
        {
            "id": uuid.uuid4(),
            "name": "admin_conocimiento",
            "description": "Administrador de conocimiento — gestiona las reglas del motor de inferencia",
            "permissions": [
                "rules:read", "rules:write", "rules:delete",
                "scenarios:read",
                "decisions:read",
                "feedback:read",
                "kpis:read",
            ],
        },
        {
            "id": uuid.uuid4(),
            "name": "decisor",
            "description": "Tomador de decisiones — crea escenarios y ejecuta análisis what-if",
            "permissions": [
                "scenarios:read", "scenarios:write", "scenarios:delete",
                "decisions:read", "decisions:write",
                "feedback:read", "feedback:write",
                "kpis:read",
            ],
        },
        {
            "id": uuid.uuid4(),
            "name": "analista",
            "description": "Analista de datos — acceso de solo lectura a KPIs y reportes",
            "permissions": [
                "kpis:read",
                "decisions:read",
                "scenarios:read",
                "feedback:read",
            ],
        },
    ]

    role_map = {}
    for role_data in roles_data:
        existing = db.query(RoleModel).filter(RoleModel.name == role_data["name"]).first()
        if existing:
            logger.info(f"  Role '{role_data['name']}' already exists, skipping.")
            role_map[role_data["name"]] = existing
        else:
            role = RoleModel(**role_data)
            db.add(role)
            db.flush()
            role_map[role_data["name"]] = role
            logger.info(f"  Created role: {role_data['name']}")

    db.commit()
    return role_map


def seed_users(db, role_map: dict) -> dict:
    """Seed users and return {username: UserModel} dict."""
    logger.info("Seeding users...")

    now = datetime.utcnow()
    users_data = [
        {
            "id": uuid.uuid4(),
            "email": "admin@nexuscorp.com",
            "username": "admin",
            "password": "admin123",
            "full_name": "Administrador del Sistema",
            "role_name": "admin_sistema",
        },
        {
            "id": uuid.uuid4(),
            "email": "knowledge@nexuscorp.com",
            "username": "knowledge",
            "password": "knowledge123",
            "full_name": "Gestor de Conocimiento",
            "role_name": "admin_conocimiento",
        },
        {
            "id": uuid.uuid4(),
            "email": "decisor@nexuscorp.com",
            "username": "decisor",
            "password": "decisor123",
            "full_name": "Tomador de Decisiones",
            "role_name": "decisor",
        },
        {
            "id": uuid.uuid4(),
            "email": "analista@nexuscorp.com",
            "username": "analista",
            "password": "analista123",
            "full_name": "Analista de Datos",
            "role_name": "analista",
        },
    ]

    user_map = {}
    for u in users_data:
        existing = db.query(UserModel).filter(UserModel.username == u["username"]).first()
        if existing:
            logger.info(f"  User '{u['username']}' already exists, skipping.")
            user_map[u["username"]] = existing
        else:
            user = UserModel(
                id=u["id"],
                email=u["email"],
                username=u["username"],
                hashed_password=hash_password(u["password"]),
                full_name=u["full_name"],
                is_active=True,
                role_id=role_map[u["role_name"]].id,
                created_at=now,
                updated_at=now,
            )
            db.add(user)
            db.flush()
            user_map[u["username"]] = user
            logger.info(f"  Created user: {u['username']} (role: {u['role_name']})")

    db.commit()
    return user_map


def seed_knowledge_rules(db, user_map: dict) -> list:
    """Seed 6 knowledge rules and return list of KnowledgeRuleModel."""
    logger.info("Seeding knowledge rules...")

    knowledge_user = user_map["knowledge"]
    now = datetime.utcnow()

    rules_data = [
        {
            "id": uuid.uuid4(),
            "name": "Stock Crítico con Demanda Alta",
            "description": "Detecta situaciones de stock insuficiente cuando la demanda es alta",
            "conditions": {
                "stock_level": {"operator": "<", "value": 20},
                "demand_level": {"operator": "==", "value": "alto"},
            },
            "action": "Generar orden de compra urgente",
            "priority": 1,
            "category": "inventario",
        },
        {
            "id": uuid.uuid4(),
            "name": "Stock Mínimo con Riesgo Alto",
            "description": "Activa proveedor de contingencia cuando el stock está en mínimos críticos",
            "conditions": {
                "stock_level": {"operator": "<", "value": 10},
                "risk_level": {"operator": "==", "value": "alto"},
            },
            "action": "Activar proveedor alternativo de emergencia",
            "priority": 1,
            "category": "riesgo",
        },
        {
            "id": uuid.uuid4(),
            "name": "Inventario Estable Demanda Media",
            "description": "Mantener el estado actual cuando hay equilibrio entre stock y demanda media",
            "conditions": {
                "demand_level": {"operator": "==", "value": "medio"},
                "stock_level": {"operator": ">", "value": 50},
            },
            "action": "Mantener inventario actual, monitorear semanalmente",
            "priority": 3,
            "category": "inventario",
        },
        {
            "id": uuid.uuid4(),
            "name": "Exceso de Stock con Demanda Baja",
            "description": "Optimiza costos reduciendo pedidos cuando hay exceso de inventario",
            "conditions": {
                "stock_level": {"operator": ">=", "value": 80},
                "demand_level": {"operator": "==", "value": "bajo"},
            },
            "action": "Reducir pedidos próximos 30 días",
            "priority": 2,
            "category": "inventario",
        },
        {
            "id": uuid.uuid4(),
            "name": "Doble Riesgo Operacional",
            "description": "Alerta crítica cuando riesgo y demanda son simultáneamente altos",
            "conditions": {
                "risk_level": {"operator": "==", "value": "alto"},
                "demand_level": {"operator": "==", "value": "alto"},
            },
            "action": "Revisar cadena de suministro inmediatamente",
            "priority": 1,
            "category": "riesgo",
        },
        {
            "id": uuid.uuid4(),
            "name": "Stock Bajo con Riesgo Medio",
            "description": "Planifica reposición preventiva para evitar desabastecimiento",
            "conditions": {
                "stock_level": {"operator": "<", "value": 30},
                "risk_level": {"operator": "==", "value": "medio"},
            },
            "action": "Planificar reposición preventiva en los próximos 7 días",
            "priority": 2,
            "category": "inventario",
        },
    ]

    rule_models = []
    for r in rules_data:
        existing = db.query(KnowledgeRuleModel).filter(KnowledgeRuleModel.name == r["name"]).first()
        if existing:
            logger.info(f"  Rule '{r['name']}' already exists, skipping.")
            rule_models.append(existing)
        else:
            rule = KnowledgeRuleModel(
                id=r["id"],
                name=r["name"],
                description=r["description"],
                conditions=r["conditions"],
                action=r["action"],
                priority=r["priority"],
                category=r["category"],
                is_active=True,
                created_by=knowledge_user.id,
                created_at=now,
                updated_at=now,
            )
            db.add(rule)
            db.flush()
            rule_models.append(rule)
            logger.info(f"  Created rule: '{r['name']}' (priority={r['priority']}, category={r['category']})")

    db.commit()
    return rule_models


def seed_scenarios(db, user_map: dict) -> list:
    """Seed 3 sample scenarios."""
    logger.info("Seeding scenarios...")

    decisor_user = user_map["decisor"]
    now = datetime.utcnow()

    scenarios_data = [
        {
            "id": uuid.uuid4(),
            "name": "Escenario Crisis Inventario Q4",
            "description": "Análisis de situación crítica de inventario para el cuarto trimestre",
            "stock_level": 15,
            "demand_level": "alto",
            "risk_level": "alto",
        },
        {
            "id": uuid.uuid4(),
            "name": "Escenario Operación Normal",
            "description": "Condiciones normales de operación con inventario equilibrado",
            "stock_level": 60,
            "demand_level": "medio",
            "risk_level": "bajo",
        },
        {
            "id": uuid.uuid4(),
            "name": "Escenario Exceso Temporada Baja",
            "description": "Exceso de inventario durante temporada de baja demanda",
            "stock_level": 85,
            "demand_level": "bajo",
            "risk_level": "bajo",
        },
    ]

    scenario_models = []
    for s in scenarios_data:
        existing = db.query(ScenarioModel).filter(ScenarioModel.name == s["name"]).first()
        if existing:
            logger.info(f"  Scenario '{s['name']}' already exists, skipping.")
            scenario_models.append(existing)
        else:
            scenario = ScenarioModel(
                id=s["id"],
                name=s["name"],
                description=s["description"],
                stock_level=s["stock_level"],
                demand_level=s["demand_level"],
                risk_level=s["risk_level"],
                created_by=decisor_user.id,
                created_at=now,
            )
            db.add(scenario)
            db.flush()
            scenario_models.append(scenario)
            logger.info(
                f"  Created scenario: '{s['name']}' "
                f"(stock={s['stock_level']}, demand={s['demand_level']}, risk={s['risk_level']})"
            )

    db.commit()
    return scenario_models


def seed_decisions_and_recommendations(db, scenario_models, rule_models, user_map):
    """Seed 2 decisions with recommendations."""
    logger.info("Seeding decisions and recommendations...")

    decisor_user = user_map["decisor"]
    now = datetime.utcnow()

    # Decision 1: Crisis scenario (scenario 0) — fires rules 0,1,4 (priority 1 rules)
    crisis_scenario = scenario_models[0]
    fired_rules_1 = [rule_models[0], rule_models[1], rule_models[4]]  # priority-1 rules

    rec_summaries_1 = [
        {"rule_id": str(r.id), "rule_name": r.name, "action": r.action, "priority": r.priority}
        for r in fired_rules_1
    ]

    existing_d1 = (
        db.query(DecisionModel)
        .filter(DecisionModel.scenario_id == crisis_scenario.id)
        .first()
    )
    if existing_d1:
        logger.info(f"  Decision for scenario '{crisis_scenario.name}' already exists, skipping.")
        decision1 = existing_d1
    else:
        decision1 = DecisionModel(
            id=uuid.uuid4(),
            scenario_id=crisis_scenario.id,
            recommendations=rec_summaries_1,
            rules_fired=[str(r.id) for r in fired_rules_1],
            status="aceptada",
            notes="Decisión crítica aceptada. Se procedió con orden de compra urgente y activación de proveedor alternativo.",
            created_by=decisor_user.id,
            created_at=now,
        )
        db.add(decision1)
        db.flush()

        for rule in fired_rules_1:
            rec = RecommendationModel(
                id=uuid.uuid4(),
                decision_id=decision1.id,
                rule_id=rule.id,
                text=rule.action,
                priority=rule.priority,
                justification=(
                    f"Regla '{rule.name}' activada. Condiciones verificadas en escenario crítico. "
                    f"Acción recomendada: {rule.action}"
                ),
                is_accepted=True,
            )
            db.add(rec)

        logger.info(f"  Created decision 1 for scenario '{crisis_scenario.name}' with {len(fired_rules_1)} recommendations")

    # Decision 2: Normal operation scenario (scenario 1) — fires rule 2
    normal_scenario = scenario_models[1]
    fired_rules_2 = [rule_models[2]]  # "Mantener inventario" rule

    rec_summaries_2 = [
        {"rule_id": str(r.id), "rule_name": r.name, "action": r.action, "priority": r.priority}
        for r in fired_rules_2
    ]

    existing_d2 = (
        db.query(DecisionModel)
        .filter(DecisionModel.scenario_id == normal_scenario.id)
        .first()
    )
    if existing_d2:
        logger.info(f"  Decision for scenario '{normal_scenario.name}' already exists, skipping.")
    else:
        decision2 = DecisionModel(
            id=uuid.uuid4(),
            scenario_id=normal_scenario.id,
            recommendations=rec_summaries_2,
            rules_fired=[str(r.id) for r in fired_rules_2],
            status="pendiente",
            notes="Operación normal detectada. Pendiente revisión mensual.",
            created_by=decisor_user.id,
            created_at=now,
        )
        db.add(decision2)
        db.flush()

        for rule in fired_rules_2:
            rec = RecommendationModel(
                id=uuid.uuid4(),
                decision_id=decision2.id,
                rule_id=rule.id,
                text=rule.action,
                priority=rule.priority,
                justification=(
                    f"Regla '{rule.name}' activada. Stock > 50 y demanda media. "
                    f"Acción: {rule.action}"
                ),
                is_accepted=False,
            )
            db.add(rec)

        logger.info(f"  Created decision 2 for scenario '{normal_scenario.name}' with {len(fired_rules_2)} recommendations")

    db.commit()


def seed_kpis(db):
    """Seed 5 KPI records."""
    logger.info("Seeding KPIs...")

    now = datetime.utcnow()
    kpis_data = [
        {
            "id": uuid.uuid4(),
            "name": "Tasa de Cumplimiento de Órdenes",
            "value": 94.5,
            "unit": "%",
            "period": "2024-Q4",
            "category": "logistica",
        },
        {
            "id": uuid.uuid4(),
            "name": "Tiempo Promedio de Entrega",
            "value": 2.3,
            "unit": "días",
            "period": "2024-Q4",
            "category": "logistica",
        },
        {
            "id": uuid.uuid4(),
            "name": "Nivel de Satisfacción del Cliente",
            "value": 4.2,
            "unit": "puntos (1-5)",
            "period": "2024-Q4",
            "category": "calidad",
        },
        {
            "id": uuid.uuid4(),
            "name": "Costo de Almacenamiento por Unidad",
            "value": 12.75,
            "unit": "USD",
            "period": "2024-Q4",
            "category": "finanzas",
        },
        {
            "id": uuid.uuid4(),
            "name": "Rotación de Inventario",
            "value": 8.1,
            "unit": "veces/año",
            "period": "2024-Q4",
            "category": "inventario",
        },
    ]

    for k in kpis_data:
        existing = db.query(KPIModel).filter(KPIModel.name == k["name"]).first()
        if existing:
            logger.info(f"  KPI '{k['name']}' already exists, skipping.")
        else:
            kpi = KPIModel(
                id=k["id"],
                name=k["name"],
                value=k["value"],
                unit=k["unit"],
                period=k["period"],
                category=k["category"],
                created_at=now,
            )
            db.add(kpi)
            logger.info(f"  Created KPI: '{k['name']}' = {k['value']} {k['unit']}")

    db.commit()


def seed_feedback(db, user_map, scenario_models):
    """Seed 2 feedback entries for existing decisions."""
    logger.info("Seeding feedback...")

    now = datetime.utcnow()
    decisor_user = user_map["decisor"]
    analista_user = user_map["analista"]

    # Get existing decisions
    decisions = db.query(DecisionModel).limit(2).all()
    if len(decisions) < 1:
        logger.warning("  No decisions found to attach feedback to, skipping feedback seed.")
        return

    feedbacks_data = [
        {
            "decision": decisions[0],
            "user": decisor_user,
            "rating": 5,
            "comment": "Excelentes recomendaciones, el sistema identificó correctamente la situación crítica y las acciones tomadas mejoraron la situación de inventario en 48 horas.",
        },
        {
            "decision": decisions[0] if len(decisions) == 1 else decisions[1],
            "user": analista_user,
            "rating": 4,
            "comment": "Buenas recomendaciones en general. El motor de reglas funcionó correctamente. Podría mejorar considerando variables externas del mercado.",
        },
    ]

    for fb_data in feedbacks_data:
        existing = (
            db.query(FeedbackModel)
            .filter(
                FeedbackModel.decision_id == fb_data["decision"].id,
                FeedbackModel.user_id == fb_data["user"].id,
            )
            .first()
        )
        if existing:
            logger.info(f"  Feedback from '{fb_data['user'].username}' already exists, skipping.")
        else:
            fb = FeedbackModel(
                id=uuid.uuid4(),
                decision_id=fb_data["decision"].id,
                user_id=fb_data["user"].id,
                rating=fb_data["rating"],
                comment=fb_data["comment"],
                created_at=now,
            )
            db.add(fb)
            logger.info(f"  Created feedback from '{fb_data['user'].username}' (rating={fb_data['rating']})")

    db.commit()


def main():
    logger.info("=" * 60)
    logger.info("Nexus-Corp KBDSS — Database Seed")
    logger.info("=" * 60)

    # Ensure tables exist
    logger.info("Creating database tables if they don't exist...")
    create_tables()

    db = SessionLocal()
    try:
        # Run all seed functions in order
        role_map = seed_roles(db)
        user_map = seed_users(db, role_map)
        rule_models = seed_knowledge_rules(db, user_map)
        scenario_models = seed_scenarios(db, user_map)
        seed_decisions_and_recommendations(db, scenario_models, rule_models, user_map)
        seed_kpis(db)
        seed_feedback(db, user_map, scenario_models)

        logger.info("=" * 60)
        logger.info("Seed completed successfully!")
        logger.info("")
        logger.info("Test credentials:")
        logger.info("  admin      / admin123      (admin_sistema)")
        logger.info("  knowledge  / knowledge123  (admin_conocimiento)")
        logger.info("  decisor    / decisor123    (decisor)")
        logger.info("  analista   / analista123   (analista)")
        logger.info("=" * 60)

    except Exception as e:
        db.rollback()
        logger.error(f"Seed failed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
