from types import SimpleNamespace

from app.services.authorization_service import AuthorizationService


def test_user_can_access_owned_resource():
    user = SimpleNamespace(
        id=10,
        role=SimpleNamespace(
            name="EMPLOYEE"
        ),
    )

    assert AuthorizationService.can_access_resource(
        user=user,
        resource_owner_id=10,
    ) is True



def test_user_cannot_access_another_users_resource():
    user = SimpleNamespace(
        id=10,
        role=SimpleNamespace(
            name="EMPLOYEE"
        ),
    )

    assert AuthorizationService.can_access_resource(
        user=user,
        resource_owner_id=20,
    ) is False



def test_admin_can_access_any_resource():
    user = SimpleNamespace(
        id=10,
        role=SimpleNamespace(
            name="ADMIN"
        ),
    )

    assert AuthorizationService.can_access_resource(
        user=user,
        resource_owner_id=20,
    ) is True



def test_auditor_can_access_any_resource():
    user = SimpleNamespace(
        id=10,
        role=SimpleNamespace(
            name="AUDITOR"
        ),
    )

    assert AuthorizationService.can_access_resource(
        user=user,
        resource_owner_id=20,
    ) is True