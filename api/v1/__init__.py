from ninja import NinjaAPI
from ninja.security import HttpBearer

from api.v1.accounts import router as accounts_router
from api.v1.images import router as images_router


class JWTAuth(HttpBearer):
    def authenticate(self, request, token: str):
        from rest_framework_simplejwt.tokens import AccessToken
        from apps.accounts.models import User

        try:
            payload = AccessToken(token)
            return User.objects.get(id=payload["user_id"])
        except Exception:
            return None


api = NinjaAPI(
    title="Pinboard API",
    version="1.0.0",
    description="Social image bookmarking platform API",
    auth=JWTAuth(),
    urls_namespace="api_v1",
)

api.add_router("/accounts/", accounts_router)
api.add_router("/images/", images_router)
