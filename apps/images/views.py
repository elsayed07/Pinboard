from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.images.forms import BookmarkForm, UploadForm
from apps.images.models import Image
from apps.images.selectors.images import ImageSelector
from apps.images.services.bookmarking import BookmarkService
from apps.images.services.engagement import EngagementService
from shared.exceptions import ApplicationError, ConflictError
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

    related = (
        ImageSelector.public_feed()
        .filter(tags__in=image.tags.all())
        .exclude(id=image.id)
        .distinct()[:8]
    )

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
    except ConflictError:
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
    except ConflictError:
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


# ── Collections ───────────────────────────────────────────────────────────────

@login_required
def collections_view(request: HttpRequest) -> HttpResponse:
    from apps.images.forms import CollectionForm
    from apps.images.models import Collection
    from apps.images.services.collections import CollectionService

    collections = (
        Collection.objects
        .filter(owner=request.user)
        .select_related("cover_image")
        .annotate(image_count=Count("images"))
        .order_by("-created_at")
    )
    form = CollectionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            col = CollectionService.create(
                owner=request.user,
                name=form.cleaned_data["name"],
                description=form.cleaned_data.get("description", ""),
                is_private=form.cleaned_data.get("is_private", False),
            )
            if request.htmx:
                col.image_count = 0
                return render(request, "components/collection_card.html", {"collection": col})
            return redirect("collections")
        except ApplicationError as exc:
            form.add_error(None, exc.message)

    return render(request, "pages/images/collections.html", {"collections": collections, "form": form})


@login_required
def collection_detail_view(request: HttpRequest, collection_id: str) -> HttpResponse:
    from apps.images.models import Collection
    collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
    images = (
        Image.objects
        .filter(collection=collection, status="ready")
        .select_related("owner", "owner__profile")
    )
    return render(request, "pages/images/collection_detail.html", {"collection": collection, "images": images})


@login_required
@require_POST
def collection_add_image_view(request: HttpRequest, collection_id: str, image_id: str) -> HttpResponse:
    from apps.images.services.collections import CollectionService
    try:
        CollectionService.add_image(user=request.user, collection_id=collection_id, image_id=image_id)
    except ApplicationError:
        pass
    return HttpResponse(status=204)


@login_required
@require_POST
def collection_remove_image_view(request: HttpRequest, image_id: str) -> HttpResponse:
    from apps.images.services.collections import CollectionService
    try:
        CollectionService.remove_image(user=request.user, image_id=image_id)
    except ApplicationError:
        pass
    return HttpResponse(status=204)
