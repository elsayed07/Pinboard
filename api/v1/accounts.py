from ninja import Router, Schema
from ninja.security import django_auth

from apps.accounts.services.auth import AuthService
from apps.accounts.services.follow import FollowService
from shared.exceptions import ApplicationError

router = Router(tags=["accounts"])


class RegisterIn(Schema):
    email: str
    username: str
    password: str


class LoginIn(Schema):
    email: str
    password: str


class TokenOut(Schema):
    access: str
    refresh: str


class ErrorOut(Schema):
    detail: str


@router.post("/register/", response={201: TokenOut, 400: ErrorOut, 409: ErrorOut}, auth=None)
def register(request, payload: RegisterIn):
    try:
        user = AuthService.register(
            email=payload.email,
            username=payload.username,
            password=payload.password,
        )
        tokens = AuthService.get_tokens_for_user(user)
        return 201, {"access": tokens.access, "refresh": tokens.refresh}
    except ApplicationError as exc:
        return exc.code, {"detail": exc.message}


@router.post("/login/", response={200: TokenOut, 400: ErrorOut}, auth=None)
def login(request, payload: LoginIn):
    try:
        user = AuthService.authenticate(email=payload.email, password=payload.password)
        tokens = AuthService.get_tokens_for_user(user)
        return 200, {"access": tokens.access, "refresh": tokens.refresh}
    except ApplicationError as exc:
        return exc.code, {"detail": exc.message}


@router.post("/follow/{target_id}/", response={201: dict, 400: ErrorOut, 404: ErrorOut, 409: ErrorOut})
def follow(request, target_id: str):
    try:
        FollowService.follow(follower=request.auth, target_id=target_id)
        return 201, {"status": "following"}
    except ApplicationError as exc:
        return exc.code, {"detail": exc.message}


@router.delete("/follow/{target_id}/", response={204: None, 404: ErrorOut})
def unfollow(request, target_id: str):
    try:
        FollowService.unfollow(follower=request.auth, target_id=target_id)
        return 204, None
    except ApplicationError as exc:
        return exc.code, {"detail": exc.message}
