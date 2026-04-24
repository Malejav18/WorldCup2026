# Sistema de Predicciones Mundial 2026

Backend de microservicios en **Python + FastAPI** con **SQLite** por servicio.
Version simplificada del diseno original (sin Kafka, sin Redis, sin Kong, sin Docker).

## Arquitectura (vista rapida)

8 microservicios de negocio + 1 API Gateway, cada uno con su propia base de datos SQLite:

| Servicio              | Puerto | BD                          |
|-----------------------|--------|-----------------------------|
| api-gateway           | 8000   | -                           |
| auth-service          | 8001   | backend/auth_service/data/auth.db |
| user-service          | 8002   | backend/user_service/data/user.db |
| tournament-service    | 8003   | backend/tournament_service/data/tournament.db |
| prediction-service    | 8004   | backend/prediction_service/data/prediction.db |
| scoring-service       | 8005   | backend/scoring_service/data/scoring.db |
| ranking-service       | 8006   | backend/ranking_service/data/ranking.db |
| league-service        | 8007   | backend/league_service/data/league.db |
| notification-service  | 8008   | backend/notification_service/data/notification.db |

**Comunicacion entre servicios:** sincrona via HTTP/REST para el flujo cliente->servicio, y asincrona via el patron **Outbox + asyncio worker** (reemplaza Kafka) para eventos de dominio como `auth.user.registered`, `match.result.registered`, etc.

Cada microservicio sigue la estructura en capas que pide el PDF:

```
<servicio>/app/
 controllers/    <- routers FastAPI (capa delgada)
 services/       <- logica de negocio
 repositories/   <- acceso a BD (SQLAlchemy)
 entities/       <- modelos SQLAlchemy (espejo del ER)
 dtos/           <- modelos Pydantic (request/response)
 workers/        <- tareas en background (outbox dispatcher)
 database.py     <- engine + session local
 config.py       <- settings (lee .env)
 main.py         <- FastAPI app + lifespan
```

## Estado actual

- [x] Fundacion compartida (`backend/shared/`): database, outbox, JWT, security, dependencia auth
- [x] `auth-service` completo (registro, login, refresh con rotacion, logout con revocacion, validate)
- [x] `tournament-service` completo (equipos, grupos, partidos, standings con desempates, terceros, registro/correccion de resultados admin)
- [x] `api-gateway` (proxy HTTP unico, CORS, mapeo de rutas por prefijo)
- [x] Seed con 48 equipos, 12 grupos, 72 partidos de fase de grupos
- [x] `user-service` (perfil publico, preferencias, stats; consume `auth.user.registered` y `scoring.user.points.updated`)
- [x] `prediction-service` (upsert predicciones de partidos, predicciones especiales, bloqueo por resultado registrado; valida partido via HTTP a tournament-service)
- [x] `scoring-service` (calcula puntos al recibir match.result.registered: 3/1/0 grupos, 4/2/0 eliminatorias; publica scoring.user.points.updated a user/ranking/notification)
- [x] `ranking-service` (consume scoring.user.points.updated; ranking global SQL indexado con paginacion y posicion del usuario; reemplaza Redis Sorted Sets del PDF)
- [x] `league-service` (crear/unirse/salir/regenerar codigo; ranking por liga enriquecido con points via user-service; publica league.member.added/removed)
- [x] `notification-service` (mocks SendGrid/FCM/APNs; consume eventos de auth, tournament, scoring y league; persiste registros y loguea con prefijo [MOCK-EMAIL]/[MOCK-PUSH])
- [x] Frontend React (Vite + TS + Tailwind + React Router + TanStack Query; login/register, dashboard, partidos con predict inline, grupos + standings, mis predicciones, ranking global paginado, ligas privadas, notificaciones, perfil)

## Requisitos

- Python 3.11+
- PowerShell (Windows) o bash

## Setup (una sola vez)

```powershell
# Desde la raiz del repo:
.\scripts\setup_venv.ps1

# Configurar variables de entorno:
Copy-Item backend\.env.example backend\.env
# (editar backend\.env si quieres cambiar el JWT_SECRET)
```

## Arrancar los servicios

Cada servicio corre en su propia ventana de PowerShell.

```powershell
# Una sola vez, cargar datos del torneo en tournament.db:
.\scripts\seed_tournament.ps1

# Todos a la vez (abre 3 ventanas de PowerShell):
.\scripts\run_all.ps1

# O individualmente:
.\scripts\run_auth_service.ps1        # puerto 8001
.\scripts\run_tournament_service.ps1  # puerto 8003
.\scripts\run_api_gateway.ps1         # puerto 8000
```

Swagger UI disponible en los 8 microservicios:
- http://127.0.0.1:8001/docs (auth), :8002 (user), :8003 (tournament), :8004 (prediction),
  :8005 (scoring), :8006 (ranking), :8007 (league), :8008 (notification)
- http://127.0.0.1:8000/routes — mapeo del api-gateway

## Frontend

SPA en React (Vite + TS + Tailwind). Apunta al gateway en :8000.

```powershell
# Una sola vez: copia config e instala deps
Copy-Item frontend\.env.example frontend\.env
# (o directamente:)
.\scripts\run_frontend.ps1   # levanta dev server en http://127.0.0.1:5173
```

La SPA expone:
- `/login` y `/register` (publicas)
- `/` (dashboard con resumen), `/matches` (predict inline), `/groups` (tablas por grupo),
  `/predictions` (mis predicciones + puntos), `/ranking` (global paginado),
  `/leagues` (crear/unirse), `/leagues/:id` (detalle + ranking), `/notifications`, `/profile`

## Probar auth-service

```powershell
# Registro
curl -X POST http://127.0.0.1:8001/auth/register `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"manuel@usa.edu.co\",\"password\":\"Password123\",\"display_name\":\"Manuel\"}'

# Login
curl -X POST http://127.0.0.1:8001/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"manuel@usa.edu.co\",\"password\":\"Password123\"}'
```

> Nota: tras el registro, el outbox intentara despachar el evento a `user-service` y `notification-service`. Como esos servicios todavia no existen, los eventos quedaran reintentandose hasta que se levanten (es el comportamiento correcto del patron).

## Decisiones de diseno vs. el PDF original

| Decision del PDF           | En este proyecto                                     | Motivo                    |
|-----------------------------|------------------------------------------------------|---------------------------|
| PostgreSQL por servicio     | SQLite por servicio                                  | Simplicidad para academico |
| Apache Kafka                | Outbox pattern + HTTP (worker asyncio)               | Sin broker externo         |
| Redis Cluster               | SQL + indices + middleware FastAPI                   | Una dependencia menos      |
| Kong API Gateway            | FastAPI gateway (fase 2)                             | Solo Python                |
| Consul + Vault              | URLs en .env                                         | Evita infraestructura      |
| JWT RS256 (clave asimetrica)| JWT HS256 (secreto compartido en .env)              | Simplifica distribucion    |
| SendGrid + FCM + APNs       | Mocks (log a consola/BD)                             | Proyecto academico         |
| Spring Boot + JPA           | FastAPI + SQLAlchemy                                 | Python                     |

## Limitaciones conocidas

- **SQLite** tiene un unico escritor concurrente por archivo. Para los "100.000 usuarios concurrentes" del PDF no serviria, pero para el proyecto academico va sobrado. Migrar a PostgreSQL mas adelante es casi transparente gracias a SQLAlchemy.
- El outbox dispatcher es **at-least-once**: si una llamada HTTP tiene exito pero el servicio consumidor crashea antes de persistir, se reintentara. Los consumidores deben ser **idempotentes** (usar claves naturales como `(userId, matchId)`).
