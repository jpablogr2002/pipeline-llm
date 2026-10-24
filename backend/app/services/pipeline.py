import logging
import time
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from app.agent.root_agent import root_agent

logger = logging.getLogger(__name__)

async def process_article_pipeline(article_data: dict):
    try:
        start_time = time.time()
        logger.info(f"Pipeline iniciado", extra={"event_type": "PIPELINE_STARTED", "article_title": article_data['title']})
        
        session_service = InMemorySessionService()
        runner = InMemoryRunner(agent=root_agent, session_service=session_service)
        
        session_id = f"art_{hash(article_data['title'])}"
        await runner.session_service.create_session(
            app_name="media_group", user_id="system", session_id=session_id
        )
        
        user_message = f"Analiza este artículo: {article_data['content']}"
        
        final_response = ""
        async for event in runner.run_async(
            user_id="system", session_id=session_id, new_message=user_message
        ):
            if event.is_final_response():
                final_response = event.content.parts[0].text
                break
        
        total_latency = int((time.time() - start_time) * 1000)
        logger.info(
            "Pipeline completado exitosamente",
            extra={
                "event_type": "PIPELINE_COMPLETED",
                "article_title": article_data['title'],
                "total_latency_ms": total_latency
            }
        )
    except Exception as e:
        logger.error(f"Error en el pipeline", extra={"event_type": "PIPELINE_ERROR", "error": str(e), "article_title": article_data['title']})