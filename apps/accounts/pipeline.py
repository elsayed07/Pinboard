"""Custom steps injected into the Social Auth pipeline."""
import httpx


def save_avatar(backend, user, response, *args, **kwargs):
    """Fetch and store the OAuth provider's profile picture on first login."""
    if hasattr(user, "profile") and user.profile.avatar:
        return

    avatar_url: str | None = None

    if backend.name == "google-oauth2":
        avatar_url = response.get("picture")
    elif backend.name == "github":
        avatar_url = response.get("avatar_url")

    if not avatar_url:
        return

    try:
        resp = httpx.get(avatar_url, timeout=5, follow_redirects=True)
        resp.raise_for_status()
    except Exception:
        return

    from django.core.files.base import ContentFile

    content = ContentFile(resp.content)
    filename = f"avatar_{user.id}.jpg"
    user.profile.avatar.save(filename, content, save=True)
