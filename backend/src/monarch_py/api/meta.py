"""Meta endpoint for serving HTML with dynamic Open Graph tags to social media crawlers."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape

from monarch_py.api.config import solr

logger = logging.getLogger(__name__)

router = APIRouter(tags=["meta"])

TEMPLATES_DIR = Path(__file__).parent / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


def get_base_url(request: Request) -> str:
    """Derive base URL from the request headers (supports beta/prod via same stack)."""
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("host", request.url.netloc)
    return f"{scheme}://{host}"


def get_default_image(request: Request) -> str:
    """Get the default OG image URL."""
    return f"{get_base_url(request)}/share-thumbnail.jpg"


@router.get("/meta/{entity_id:path}", response_class=HTMLResponse)
async def get_meta_page(entity_id: str, request: Request) -> HTMLResponse:
    """
    Return an HTML page with dynamic Open Graph meta tags for the given entity.

    This endpoint is designed to be called by social media crawlers (Slackbot,
    Twitterbot, etc.) to get entity-specific link previews. Regular users
    should be served the SPA directly by Nginx.

    Args:
        entity_id: The entity identifier (e.g., MONDO:0005148)
        request: The FastAPI request object

    Returns:
        HTML page with entity-specific OG meta tags

    Raises:
        HTTPException: 404 if entity not found
    """
    try:
        entity = solr().get_entity(entity_id, extra=False)
    except Exception as e:
        logger.warning(f"Failed to fetch entity {entity_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Entity not found: {entity_id}")

    if entity is None:
        raise HTTPException(status_code=404, detail=f"Entity not found: {entity_id}")

    base_url = get_base_url(request)
    entity_url = f"{base_url}/{entity_id}"

    entity_name = entity.name or entity_id
    title = f"{entity_name} | Monarch Initiative"

    description_parts = []
    if entity.name:
        description_parts.append(entity.name)
    if entity.description:
        description_parts.append(entity.description)

    if description_parts:
        description = " - ".join(description_parts)
    else:
        description = f"View {entity_id} on Monarch Initiative"

    max_description_length = 300
    if len(description) > max_description_length:
        description = description[: max_description_length - 3] + "..."

    template = jinja_env.get_template("meta.html")
    html_content = template.render(
        title=title,
        description=description,
        url=entity_url,
        image=get_default_image(request),
    )

    return HTMLResponse(content=html_content, status_code=200)
