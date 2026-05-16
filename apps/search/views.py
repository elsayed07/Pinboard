from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.search.services import SearchService


def search_view(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip()
    tag = request.GET.get("tag", "").strip()
    results = []

    if query:
        results = SearchService.search_images(query)
    elif tag:
        results = SearchService.search_by_tag(tag)

    if request.htmx:
        return render(request, "components/image_grid.html", {"page": {"results": results}})
    return render(request, "pages/search/results.html", {
        "results": results,
        "query": query,
        "tag": tag,
    })
