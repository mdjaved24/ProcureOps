from types import SimpleNamespace

import pytest

from app.ai.services.agent_authorization_service import (
    AgentAuthorizationService,
)


def make_user(permission_codes: list[str]):
    permissions = [
        SimpleNamespace(code=code)
        for code in permission_codes
    ]

    role = SimpleNamespace(
        permissions=permissions,
    )

    return SimpleNamespace(
        id=101,
        role=role,
    )


# ==========================================================
# APPROVE
# ==========================================================

def test_user_with_approve_permission_is_authorized():
    user = make_user(
        ["approval:approve"]
    )

    assert (
        AgentAuthorizationService.has_permission(
            user=user,
            action="APPROVE_QUOTATION",
        )
        is True
    )


def test_user_without_approve_permission_is_not_authorized():
    user = make_user(
        ["approval:read"]
    )

    assert (
        AgentAuthorizationService.has_permission(
            user=user,
            action="APPROVE_QUOTATION",
        )
        is False
    )


# ==========================================================
# REJECT
# ==========================================================

def test_user_with_reject_permission_is_authorized():
    user = make_user(
        ["approval:reject"]
    )

    assert (
        AgentAuthorizationService.has_permission(
            user=user,
            action="REJECT_QUOTATION",
        )
        is True
    )


def test_user_without_reject_permission_is_not_authorized():
    user = make_user(
        ["approval:read"]
    )

    assert (
        AgentAuthorizationService.has_permission(
            user=user,
            action="REJECT_QUOTATION",
        )
        is False
    )


# ==========================================================
# MULTIPLE PERMISSIONS
# ==========================================================

def test_user_with_multiple_permissions_is_authorized():
    user = make_user(
        [
            "approval:read",
            "approval:approve",
            "approval:reject",
        ]
    )

    assert (
        AgentAuthorizationService.has_permission(
            user=user,
            action="APPROVE_QUOTATION",
        )
        is True
    )

    assert (
        AgentAuthorizationService.has_permission(
            user=user,
            action="REJECT_QUOTATION",
        )
        is True
    )


# ==========================================================
# UNKNOWN ACTION
# ==========================================================

def test_unknown_action_is_not_authorized():
    user = make_user(
        ["approval:approve"]
    )

    assert (
        AgentAuthorizationService.has_permission(
            user=user,
            action="DELETE_QUOTATION",
        )
        is False
    )


# ==========================================================
# REQUIRE PERMISSION
# ==========================================================

def test_require_permission_does_not_raise_when_authorized():
    user = make_user(
        ["approval:approve"]
    )

    AgentAuthorizationService.require_permission(
        user=user,
        action="APPROVE_QUOTATION",
    )


def test_require_permission_raises_when_not_authorized():
    user = make_user(
        ["approval:read"]
    )

    with pytest.raises(PermissionError):
        AgentAuthorizationService.require_permission(
            user=user,
            action="APPROVE_QUOTATION",
        )