from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from apps.accounts.forms import AvatarForm, LoginForm, ProfileForm, RegisterForm
from apps.accounts.models import User
from apps.accounts.selectors.users import UserSelector
from apps.accounts.services.auth import AuthService
from apps.accounts.services.follow import FollowService
from apps.accounts.services.profile import ProfileService
from apps.accounts.tasks import send_welcome_email
from shared.exceptions import ApplicationError
from shared.pagination import paginate


@ratelimit(key="ip", rate="10/h", method="POST", block=True)
def register_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("home")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            user = AuthService.register(
                email=form.cleaned_data["email"],
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            send_welcome_email.delay(str(user.id))
            return redirect("home")
        except ApplicationError as exc:
            form.add_error(None, exc.message)

    return render(request, "pages/auth/register.html", {"form": form})


@ratelimit(key="ip", rate="20/h", method="POST", block=True)
def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("home")

    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            user = AuthService.authenticate(
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            next_url = request.GET.get("next", "home")
            return redirect(next_url)
        except ApplicationError as exc:
            form.add_error(None, exc.message)

    return render(request, "pages/auth/login.html", {"form": form})


@require_POST
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("login")


def profile_view(request: HttpRequest, username: str) -> HttpResponse:
    profile_user = get_object_or_404(User.objects.select_related("profile"), username=username)
    viewer = request.user if request.user.is_authenticated else None

    is_following = False
    if viewer and not viewer.is_anonymous and viewer.pk != profile_user.pk:
        is_following = UserSelector.is_following(follower=viewer, target=profile_user)

    from apps.images.selectors.images import ImageSelector
    qs = ImageSelector.user_images(owner=profile_user, viewer=viewer)
    page = paginate(qs, page=int(request.GET.get("page", 1)))

    if request.htmx:
        return render(request, "components/image_grid.html", {"page": page})
    return render(request, "pages/profile/detail.html", {
        "profile_user": profile_user,
        "is_following": is_following,
        "page": page,
        "follower_count": profile_user.followers.count(),
        "following_count": profile_user.following.count(),
    })


@login_required
def settings_view(request: HttpRequest) -> HttpResponse:
    profile = request.user.profile
    form = ProfileForm(request.POST or None, initial={
        "full_name": profile.full_name,
        "bio": profile.bio,
        "website": profile.website,
        "location": profile.location,
        "privacy_level": profile.privacy_level,
    })

    if request.method == "POST" and form.is_valid():
        ProfileService.update_profile(
            request.user,
            full_name=form.cleaned_data["full_name"],
            bio=form.cleaned_data["bio"],
            website=form.cleaned_data["website"],
            location=form.cleaned_data["location"],
            privacy_level=form.cleaned_data["privacy_level"],
        )
        messages.success(request, "Profile updated.")
        if request.htmx:
            return HttpResponse(status=204, headers={"HX-Trigger": "profileUpdated"})
        return redirect("settings")

    return render(request, "pages/profile/settings.html", {"form": form, "profile": profile})


@login_required
@require_POST
def update_avatar_view(request: HttpRequest) -> HttpResponse:
    form = AvatarForm(request.POST, request.FILES)
    if form.is_valid():
        ProfileService.update_avatar(request.user, form.cleaned_data["avatar"])
        messages.success(request, "Avatar updated.")
    return redirect("settings")


@login_required
@require_POST
def follow_view(request: HttpRequest, username: str) -> HttpResponse:
    target = get_object_or_404(User, username=username)
    try:
        FollowService.follow(follower=request.user, target_id=str(target.id))
        is_following = True
    except ApplicationError:
        is_following = True

    if request.htmx:
        return render(request, "components/follow_button.html", {
            "profile_user": target,
            "is_following": is_following,
        })
    return redirect("profile", username=username)


@login_required
@require_POST
def unfollow_view(request: HttpRequest, username: str) -> HttpResponse:
    target = get_object_or_404(User, username=username)
    try:
        FollowService.unfollow(follower=request.user, target_id=str(target.id))
    except ApplicationError:
        pass

    if request.htmx:
        return render(request, "components/follow_button.html", {
            "profile_user": target,
            "is_following": False,
        })
    return redirect("profile", username=username)


@login_required
@require_POST
def block_view(request: HttpRequest, username: str) -> HttpResponse:
    target = get_object_or_404(User, username=username)
    try:
        FollowService.block(blocker=request.user, target_id=str(target.id))
    except ApplicationError:
        pass
    return redirect("home")


@login_required
@require_POST
def unblock_view(request: HttpRequest, username: str) -> HttpResponse:
    target = get_object_or_404(User, username=username)
    FollowService.unblock(blocker=request.user, target_id=str(target.id))
    return redirect("profile", username=username)


@login_required
def saved_images_view(request: HttpRequest) -> HttpResponse:
    from apps.images.models import Image
    qs = (
        Image.objects.filter(saves__user=request.user, status="ready")
        .select_related("owner", "owner__profile")
        .prefetch_related("tags")
        .order_by("-saves__created_at")
    )
    page = paginate(qs, page=int(request.GET.get("page", 1)))
    if request.htmx:
        return render(request, "components/image_grid.html", {"page": page})
    return render(request, "pages/profile/saved.html", {"page": page})


@login_required
def liked_images_view(request: HttpRequest) -> HttpResponse:
    from apps.images.models import Image
    qs = (
        Image.objects.filter(likes__user=request.user, status="ready")
        .select_related("owner", "owner__profile")
        .prefetch_related("tags")
        .order_by("-likes__created_at")
    )
    page = paginate(qs, page=int(request.GET.get("page", 1)))
    if request.htmx:
        return render(request, "components/image_grid.html", {"page": page})
    return render(request, "pages/profile/liked.html", {"page": page})
