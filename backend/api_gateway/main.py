"""api-gateway: proxy HTTP unico para el frontend.

Estrategia:
  - El frontend siempre le pega a http://localhost:8000/*
  - El gateway mapea prefijos de ruta a URLs de microservicios (configurables en .env)
  - Se preservan headers (Authorization, Content-Type) y query string
  - Cada microservicio valida su propio JWT con el secreto compartido (ver
    shared/auth_dependency.py). El gateway NO decodifica JWT; solo rutea.
  - CORS abierto en dev; en prod restringir a los origenes del frontend.

No se implementan rate limiting ni JWT validation a nivel de gateway en esta
version; son agregables como middlewares cuando se necesiten.

Ejecutar desde `backend/`:
    python -m uvicorn api_gateway.main:app --host 127.0.0.1 --port 8000 --reload
"""
import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware

from api_gateway.config import settings


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("api-gateway")


# Mapeo prefijo-de-ruta -> URL downstream. Orden relevante: prefijos mas
# especificos primero. Las rutas internas (/internal/*) NO se exponen aqui.
ROUTES: list[tuple[str, str]] = [
    ("/auth", settings.auth_service_url),
    ("/users", settings.user_service_url),
    ("/tournament", settings.tournament_service_url),
    ("/predictions", settings.prediction_service_url),
    ("/scoring", settings.scoring_service_url),
    ("/rankings", settings.ranking_service_url),
    ("/leagues", settings.league_service_url),
    ("/notifications", settings.notification_service_url),
]

# Headers que NO se reenvian (hop-by-hop o los controla httpx/FastAPI).
HOP_BY_HOP_HEADERS = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade",
    "host", "content-length",
}


def _resolve_downstream(path: str) -> tuple[str, str] | None:
    for prefix, base in ROUTES:
        if path == prefix or path.startswith(prefix + "/"):
            return base, path
    return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient(timeout=30.0)
    try:
        yield
    finally:
        await app.state.http.aclose()


app = FastAPI(title=settings.service_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restringir en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["infra"])
def health() -> dict:
    return {"status": "ok", "service": settings.service_name}


@app.get("/routes", tags=["infra"])
def list_routes() -> dict:
    return {"routes": [{"prefix": p, "target": u} for p, u in ROUTES]}


@app.api_route(
    "/{full_path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    include_in_schema=False,
)
async def proxy(full_path: str, request: Request) -> Response:
    path = "/" + full_path
    resolved = _resolve_downstream(path)
    if resolved is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No route for {path}")

    base_url, downstream_path = resolved
    url = f"{base_url.rstrip('/')}{downstream_path}"

    headers = {k: v for k, v in request.headers.items() if k.lower() not in HOP_BY_HOP_HEADERS}
    body = await request.body()

    client: httpx.AsyncClient = request.app.state.http
    try:
        downstream_response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
            params=request.query_params,
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Downstream service unreachable: {base_url}",
        )
    except httpx.HTTPError as e:
        logger.exception("Proxy request failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    response_headers = {
        k: v for k, v in downstream_response.headers.items()
        if k.lower() not in HOP_BY_HOP_HEADERS
    }
    return Response(
        content=downstream_response.content,
        status_code=downstream_response.status_code,
        headers=response_headers,
        media_type=downstream_response.headers.get("content-type"),
    )
