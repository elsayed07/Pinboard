from typing import Any
from ninja import Router, Schema, UploadedFile, File
from ninja.pagination import paginate, PageNumberPagination

from apps.images.selectors.images import ImageSelector
from apps.images.services.bookmarking import BookmarkService
from apps.images.services.engagement import EngagementService
from shared.exceptions import ApplicationError

router = Router(tags=["images"])


class BookmarkIn(Schema):
    url: str
    title: str
    description: str = ""
    tags: list[str] = []


class ImageOut(Schema):
    id: str
    title: str
    slug: str
    thumbnail_url: str | None
    like_count: int
    view_count: int
    owner_username: str

    @staticmethod
    def resolve_id(obj) -> str:
        return str(obj.id)

    @staticmethod
    def resolve_thumbnail_url(obj) -> str | None:
        return obj.thumbnail.url if obj.thumbnail else None

    @staticmethod
    def resolve_owner_username(obj) -> str:
        return obj.owner.username


class ErrorOut(Schema):
    detail: str


@router.get("/feed/", response=list[ImageOut])
@paginate(PageNumberPagination, page_size=24)
def feed(request):
    return ImageSelector.following_feed(user=request.auth)


@router.get("/trending/", response=list[ImageOut], auth=None)
def trending(request):
    return ImageSelector.trending()


@router.post("/bookmark/", response={201: ImageOut, 400: ErrorOut, 422: ErrorOut})
def bookmark(request, payload: BookmarkIn):
    try:
        image = BookmarkService.bookmark_from_url(
            owner=request.auth,
            url=payload.url,
            title=payload.title,
            description=payload.description,
            tags=payload.tags or None,
        )
        return 201, image
    except ApplicationError as exc:
        return exc.code, {"detail": exc.message}


@router.post("/{image_id}/like/", response={201: dict, 400: ErrorOut, 409: ErrorOut})
def like(request, image_id: str):
    try:
        EngagementService.like(user=request.auth, image_id=image_id)
        return 201, {"status": "liked"}
    except ApplicationError as exc:
        return exc.code, {"detail": exc.message}


@router.delete("/{image_id}/like/", response={204: None, 404: ErrorOut})
def unlike(request, image_id: str):
    try:
        EngagementService.unlike(user=request.auth, image_id=image_id)
        return 204, None
    except ApplicationError as exc:
        return exc.code, {"detail": exc.message}


@router.post("/{image_id}/view/", response={200: dict}, auth=None)
def record_view(request, image_id: str):
    count = EngagementService.record_view(image_id=image_id)
    return 200, {"views": count}
