from app.models.identity.user import User


class AuthorizationService:

    @staticmethod
    def is_resource_owner(
        user: User,
        resource_owner_id: int,
    ) -> bool:
        return user.id == resource_owner_id

    @staticmethod
    def can_access_resource(
        user: User,
        resource_owner_id: int,
    ) -> bool:
        if user.role.name in {
            "ADMIN",
            "AUDITOR",
        }:
            return True

        return user.id == resource_owner_id