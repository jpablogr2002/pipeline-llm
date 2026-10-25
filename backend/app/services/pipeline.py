
import logging
import time
import uuid

from google.genai import types
from google.adk.runners import InMemoryRunner
from app.agent.root_agent import root_agent
from app.services.db import guardar_analisis

logger = logging.getLogger(__name__)

APP_NAME = "media_group"
USER_ID = "system"

RESULTS_DB = {}
HISTORIAL_ANALISIS = {}

async def process_article_pipeline(article_data: dict, task_id: str):
    start_time = time.time()

    try:
        logger.info(
            "Pipeline iniciado",
            extra={
                "event_type": "PIPELINE_STARTED",
                "article_title": article_data["title"],
            },
        )

        runner = InMemoryRunner(
            agent=root_agent,
            app_name=APP_NAME,
        )

        session_id = f"art_{uuid.uuid4().hex}"

        # Crear la sesión en el servicio del mismo runner.
        session = await runner.session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id,
        )

        # Verificar que la sesión se encuentre disponible.
        verified_session = await runner.session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session.id,
        )

        if verified_session is None:
            raise RuntimeError(
                f"La sesión no existe después de crearla: {session.id}"
            )

        logger.info(
            "Sesión creada y verificada",
            extra={
                "session_id": session.id,
                "app_name": APP_NAME,
                "user_id": USER_ID,
            },
        )

        user_content = types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=f"Analiza este artículo: {article_data['content']}"
                )
            ],
        )

        final_response = ""

        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=user_content,
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = (
                        event.content.parts[0].text or ""
                    )
                break

        total_latency = int((time.time() - start_time) * 1000)

        RESULTS_DB[task_id] = {
            "status": "completed",
            "result": final_response,
            "latency_ms": total_latency,
        }

        analisis_data = {
            "article_title": article_data["title"],
            "result": final_response,
            "latency_ms": total_latency,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        guardar_analisis(task_id, analisis_data)

        logger.info(
            "Pipeline completado exitosamente",
            extra={
                "event_type": "PIPELINE_COMPLETED",
                "article_title": article_data["title"],
                "total_latency_ms": total_latency,
                "session_id": session.id,
                "agent_response": final_response
            },
        )

        return final_response

    except Exception:
        logger.exception(
            "Error en el pipeline",
            extra={
                "event_type": "PIPELINE_ERROR",
                "article_title": article_data.get("title", "unknown"),
            },
        )
        raise
