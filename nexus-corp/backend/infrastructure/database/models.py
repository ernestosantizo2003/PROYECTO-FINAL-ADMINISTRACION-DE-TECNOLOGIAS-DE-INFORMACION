import uuid
from datetime import datetime
from typing import List

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.connection import Base


class RoleModel(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    permissions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # Relationships
    users: Mapped[List["UserModel"]] = relationship("UserModel", back_populates="role")

    def __repr__(self) -> str:
        return f"<Role {self.name}>"


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    role: Mapped["RoleModel"] = relationship("RoleModel", back_populates="users")
    scenarios: Mapped[List["ScenarioModel"]] = relationship(
        "ScenarioModel", back_populates="creator"
    )
    decisions: Mapped[List["DecisionModel"]] = relationship(
        "DecisionModel", back_populates="creator"
    )
    feedbacks: Mapped[List["FeedbackModel"]] = relationship(
        "FeedbackModel", back_populates="user"
    )
    audit_logs: Mapped[List["AuditLogModel"]] = relationship(
        "AuditLogModel", back_populates="user"
    )
    knowledge_rules: Mapped[List["KnowledgeRuleModel"]] = relationship(
        "KnowledgeRuleModel", back_populates="creator"
    )

    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class KnowledgeRuleModel(Base):
    __tablename__ = "knowledge_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    conditions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=2)  # 1=alta,2=media,3=baja
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="general")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    creator: Mapped["UserModel"] = relationship("UserModel", back_populates="knowledge_rules")

    __table_args__ = (
        Index("ix_rules_active", "is_active"),
        Index("ix_rules_category", "category"),
        Index("ix_rules_priority", "priority"),
    )

    def __repr__(self) -> str:
        return f"<KnowledgeRule {self.name}>"


class ScenarioModel(Base):
    __tablename__ = "scenarios"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    stock_level: Mapped[int] = mapped_column(Integer, nullable=False)
    demand_level: Mapped[str] = mapped_column(String(20), nullable=False)  # bajo|medio|alto
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)    # bajo|medio|alto
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )

    # Relationships
    creator: Mapped["UserModel"] = relationship("UserModel", back_populates="scenarios")
    decisions: Mapped[List["DecisionModel"]] = relationship(
        "DecisionModel", back_populates="scenario"
    )

    def __repr__(self) -> str:
        return f"<Scenario {self.name}>"


class DecisionModel(Base):
    __tablename__ = "decisions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scenarios.id"), nullable=False
    )
    recommendations: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    rules_fired: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pendiente"
    )  # pendiente|aceptada|rechazada
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )

    # Relationships
    scenario: Mapped["ScenarioModel"] = relationship("ScenarioModel", back_populates="decisions")
    creator: Mapped["UserModel"] = relationship("UserModel", back_populates="decisions")
    recommendation_records: Mapped[List["RecommendationModel"]] = relationship(
        "RecommendationModel", back_populates="decision"
    )
    feedbacks: Mapped[List["FeedbackModel"]] = relationship(
        "FeedbackModel", back_populates="decision"
    )

    __table_args__ = (
        Index("ix_decisions_status", "status"),
        Index("ix_decisions_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Decision {self.id} status={self.status}>"


class RecommendationModel(Base):
    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    decision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("decisions.id"), nullable=False
    )
    rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("knowledge_rules.id"), nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=False, default="")
    is_accepted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    decision: Mapped["DecisionModel"] = relationship(
        "DecisionModel", back_populates="recommendation_records"
    )

    __table_args__ = (
        Index("ix_recommendations_decision_id", "decision_id"),
        Index("ix_recommendations_is_accepted", "is_accepted"),
    )

    def __repr__(self) -> str:
        return f"<Recommendation {self.id}>"


class FeedbackModel(Base):
    __tablename__ = "feedback"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    decision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("decisions.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )

    # Relationships
    decision: Mapped["DecisionModel"] = relationship("DecisionModel", back_populates="feedbacks")
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="feedbacks")

    __table_args__ = (
        Index("ix_feedback_decision_id", "decision_id"),
        Index("ix_feedback_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<Feedback rating={self.rating}>"


class KPIModel(Base):
    __tablename__ = "kpis"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    period: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )

    __table_args__ = (
        Index("ix_kpis_category", "category"),
    )

    def __repr__(self) -> str:
        return f"<KPI {self.name}={self.value}>"


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # CREATE|UPDATE|DELETE
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    details: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="audit_logs")

    __table_args__ = (
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_entity_type", "entity_type"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} {self.entity_type}>"
