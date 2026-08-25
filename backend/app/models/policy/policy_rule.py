from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class PolicyRule(Base):
    __tablename__ = "policy_rules"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    policy_id = Column(
        Integer,
        ForeignKey(
            "policies.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    rule_code = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    name = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    priority = Column(
        Integer,
        nullable=False,
        default=100,
    )

    condition = Column(
    JSON,
    nullable=False,
    )

    action = Column(
        JSON,
        nullable=False,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    policy = relationship(
        "Policy",
    )