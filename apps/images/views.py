from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.images.forms import BookmarkForm, UploadForm
from apps.images.models import Image
from apps.images.selectors.images import ImageSelector
from apps.images.services.bookmarking import BookmarkService
from apps.images.services.engagement import EngagementService
from shared.exceptions import ApplicationError
from shared.pagination import paginate


def home_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        qs = ImageSelector.following_feed(user=request.user)
        if not qs.exists():
            qs = ImageSelector.public_feed()
        template = "pages/images/feed.html"
    else:
        qs = ImageSelector.public_feed()
        template = "pages/images/discover.html"

    page = paginate(qs, page=int(request.GET.get("page", 1)))

    if request.htmx:
        return render(request, "components/image_grid.html", {"page": page})
    return render(request, template, {"page": page})


def discover_view(request: HttpRequest) -> HttpResponse:
    qs = ImageSelector.trending()
    page = paginate(qs)
    if request.htmx:
        return render(request, "components/image_grid.html", {"page": page})
    return render(request, "pages/images/discover.html", {"page": page})


def image_detail_view(request: HttpRequest, slug: str) -> HttpResponse:
    image = get_object_or_404(
        Image.objects.select_related("owner", "owner__profile", "collection").prefetch_related("tags"),
        slug=slug,
        status="ready",
    )
    EngagementService.record_view(image_id=str(image.id))

    user_liked = False
    user_saved = False
    if request.user.is_authenticated:
        user_liked = image.likes.filter(user=request.user).exists()
        user_saved = image.saves.filter(user=request.user).exists()

    related = ImageSelector.public_feed().filter(tags__in=image.tags.all()).exclude(id=image.id).distinct()[:8]

    return render(request, "pages/images/detail.html", {
        "image": image,
        "user_liked": user_liked,
        "user_saved": user_saved,
        "related": related,
    })


@login_required
def bookmark_view(request: HttpRequest) -> HttpResponse:
    form = BookmarkForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            image = BookmarkService.bookmark_from_url(
                owner=request.user,
                url=form.cleaned_data["url"],
                title=form.cleaned_data["title"],
                description=form.cleaned_data.get("description", ""),
                tags=form.cleaned_data.get("tags", []),
            )
            return redirect("image-detail", slug=image.slug)
        except ApplicationError as exc:
            form.add_error(None, exc.message)
    return render(request, "pages/images/bookmark.html", {"form": form})


@login_required
def upload_view(request: HttpRequest) -> HttpResponse:
    form = UploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        try:
            image = BookmarkService.upload_image(
                owner=request.user,
                file=form.cleaned_data["image"],
                title=form.cleaned_data["title"],
                description=form.cleaned_data.get("description", ""),
                tags=form.cleaned_data.get("tags", []),
            )
            return redirect("image-detail", slug=image.slug)
        except ApplicationError as exc:
            form.add_error(None, exc.message)
    return render(request, "pages/images/upload.html", {"form": form})


@login_required
@require_POST
def like_view(request: HttpRequest, image_id: str) -> HttpResponse:
    try:
        EngagementService.like(user=request.user, image_id=image_id)
        liked = True
    except ApplicationError:
        liked = True

    image = get_object_or_404(Image, id=image_id)
    if request.htmx:
        return render(request, "components/like_button.html", {"image": image, "user_liked": liked})
    return redirect("image-detail", slug=image.slug)


@login_required
@require_POST
def unlike_view(request: HttpRequest, image_id: str) -> HttpResponse:
    try:
        EngagementService.unlike(user=request.user, image_id=image_id)
    except ApplicationError:
        pass

    image = get_object_or_404(Image, id=image_id)
    if request.htmx:
        return render(request, "components/like_button.html", {"image": image, "user_liked": False})
    return redirect("image-detail", slug=image.slug)


@login_required
@require_POST
def save_view(request: HttpRequest, image_id: str) -> HttpResponse:
    try:
        EngagementService.save_image(user=request.user, image_id=image_id)
        saved = True
    except ApplicationError:
        saved = True

    image = get_object_or_404(Image, id=image_id)
    if request.htmx:
        return render(request, "components/save_button.html", {"image": image, "user_saved": saved})
    return redirect("image-detail", slug=image.slug)


@login_required
@require_POST
def unsave_view(request: HttpRequest, image_id: str) -> HttpResponse:
    try:
        EngagementService.unsave_image(user=request.user, image_id=image_id)
    except ApplicationError:
        pass

    image = get_object_or_404(Image, id=image_id)
    if request.htmx:
        return render(request, "components/save_button.html", {"image": image, "user_saved": False})
    return redirect("image-detail", slug=image.slug)
