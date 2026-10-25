from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import verify_password, get_user, create_access_token, fake_users_db
from app.services.pipeline import process_article_pipeline, RESULTS_DB
from app.services.db import obtener_historial, calcular_metricas

import logging
import uuid

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")
logger = logging.getLogger("app.api")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/auth/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(fake_users_db, form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

class ArticlePayload(BaseModel):
    title: str
    content: str
    source_url: str

@router.post("/webhook/ingest")
@limiter.limit("5/minute")
async def ingest_article(
    request: Request,
    payload: ArticlePayload, 
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    task_id = str(uuid.uuid4())
    background_tasks.add_task(process_article_pipeline, payload.model_dump(), task_id)
    logger.info(
        "Webhook recibido",
        extra={"event_type": "WEBHOOK_RECEIVED", "user": current_user["username"]}
    )
    return {"status": "received", "task_id": task_id}

@router.get("/webhook/result/{task_id}")
async def get_result(task_id: str, current_user: dict = Depends(get_current_user)):
    result = RESULTS_DB.get(task_id)
    if not result:
        return {"status": "processing"} # Aún no termina
    
    return result

@router.get("/dashboard/metrics")
async def get_dashboard_metrics(current_user: dict = Depends(get_current_user)):
    # Consultamos las métricas reales a Firestore
    metricas = calcular_metricas()
    historial_reciente = obtener_historial(limite=5) # Últimos 5

    return {
        "total_procesados": metricas["total_procesados"],
        "latencia_promedio_ms": metricas["latencia_promedio_ms"],
        "costo_estimado_usd": metricas["costo_estimado_usd"],
        "historial": historial_reciente
    }