"""
Rule Engine for Nexus-Corp KBDSS.

Evaluates knowledge rules against a scenario and returns a list of matched results.

Supported condition fields:
  - stock_level    (int)
  - demand_level   (str: bajo|medio|alto)
  - risk_level     (str: bajo|medio|alto)

Supported operators:
  - <, <=, >, >=, ==, !=

Condition JSON format:
  {
    "stock_level": {"operator": "<", "value": 20},
    "demand_level": {"operator": "==", "value": "alto"}
  }
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import UUID

from core.logging_config import get_logger
from domain.entities.knowledge_rule import KnowledgeRule
from domain.repositories.knowledge_rule_repository import KnowledgeRuleRepository

logger = get_logger(__name__)


@dataclass
class RuleResult:
    rule_id: UUID
    rule_name: str
    action: str
    priority: int
    justification: str
    matched_conditions: List[str] = field(default_factory=list)


def _evaluate_condition(field_value: Any, operator: str, condition_value: Any) -> bool:
    """Evaluate a single condition against a field value."""
    try:
        if operator == "<":
            return field_value < condition_value
        elif operator == "<=":
            return field_value <= condition_value
        elif operator == ">":
            return field_value > condition_value
        elif operator == ">=":
            return field_value >= condition_value
        elif operator == "==":
            return field_value == condition_value
        elif operator == "!=":
            return field_value != condition_value
        else:
            logger.warning(f"Unknown operator '{operator}', skipping condition")
            return False
    except TypeError as e:
        logger.warning(f"Type error evaluating condition: {e}")
        return False


def _evaluate_rule(rule: KnowledgeRule, scenario: Dict[str, Any]) -> Optional[RuleResult]:
    """
    Evaluate a single rule against the scenario.
    Returns RuleResult if all conditions match, None otherwise.
    """
    conditions: Dict[str, Any] = rule.conditions
    matched_conditions: List[str] = []
    all_matched = True

    for field_name, condition in conditions.items():
        if not isinstance(condition, dict):
            logger.warning(f"Invalid condition format for field '{field_name}' in rule '{rule.name}'")
            all_matched = False
            break

        operator = condition.get("operator")
        condition_value = condition.get("value")

        if operator is None or condition_value is None:
            logger.warning(f"Missing operator/value in condition for field '{field_name}' in rule '{rule.name}'")
            all_matched = False
            break

        field_value = scenario.get(field_name)
        if field_value is None:
            logger.debug(f"Field '{field_name}' not found in scenario, skipping rule '{rule.name}'")
            all_matched = False
            break

        if not _evaluate_condition(field_value, operator, condition_value):
            all_matched = False
            break

        # Build human-readable condition description
        matched_conditions.append(
            f"{field_name} {operator} {condition_value} (actual: {field_value})"
        )

    if not all_matched:
        return None

    # Build justification string
    justification = (
        f"Regla '{rule.name}' activada porque: "
        + " Y ".join(matched_conditions)
        + f". Acción recomendada: {rule.action}"
    )

    return RuleResult(
        rule_id=rule.id,
        rule_name=rule.name,
        action=rule.action,
        priority=rule.priority,
        justification=justification,
        matched_conditions=matched_conditions,
    )


class RuleEngine:
    """
    Forward-chaining rule engine.
    Evaluates all active rules against a given scenario.
    """

    def __init__(self, rule_repository: KnowledgeRuleRepository):
        self.rule_repository = rule_repository

    def evaluate(self, scenario: Dict[str, Any]) -> List[RuleResult]:
        """
        Evaluate all active rules against the scenario.

        Args:
            scenario: dict with keys stock_level (int), demand_level (str), risk_level (str)

        Returns:
            List of RuleResult sorted by priority (1=alta first)
        """
        logger.info(f"Running rule engine against scenario: {scenario}")

        active_rules: List[KnowledgeRule] = self.rule_repository.list_active()
        logger.info(f"Loaded {len(active_rules)} active rules")

        results: List[RuleResult] = []

        for rule in active_rules:
            try:
                result = _evaluate_rule(rule, scenario)
                if result:
                    results.append(result)
                    logger.info(
                        f"Rule '{rule.name}' FIRED → priority={rule.priority}, action='{rule.action}'"
                    )
                else:
                    logger.debug(f"Rule '{rule.name}' did not fire")
            except Exception as e:
                logger.error(f"Error evaluating rule '{rule.name}': {e}", exc_info=True)

        # Sort by priority ascending (1=alta before 3=baja)
        results.sort(key=lambda r: r.priority)

        logger.info(f"Rule engine completed. {len(results)} rules fired out of {len(active_rules)}")
        return results
