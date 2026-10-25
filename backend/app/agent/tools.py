import os
import time
import logging 
import vertexai
from vertexai.generative_models import GenerativeModel
from app.core.resilience import llm_circuit_breaker

vertexai.init(project=os.getenv("GCP_PROJECT_ID"), location=os.getenv("GCP_REGION"))
logger = logging.getLogger("app.agent.tools")

def analizar_con_llm(texto: str) -> str:
    """Analiza un texto usando Vertex AI para extraer categoría y resumen SEO."""
    start_time = time.time()

    # Definimos la función interna que será protegida por el Circuit Breaker
    def _call_vertex_ai():
        model = GenerativeModel("gemini-3.5-flash")
        prompt = f"Analiza este artículo y devuelve JSON con categoria, sentimiento y resumen_seo (max 160 chars): {texto[:2000]}"
        response = model.generate_content(prompt)
        return response

    try:
        # Envolvemos la llamada con el Circuit Breaker
        response = llm_circuit_breaker.call(_call_vertex_ai)
        
        # Calcular latencia y estimar tokens (aprox 4 caracteres = 1 token)
        latency_ms = int((time.time() - start_time) * 1000)
        tokens_in = len(texto) // 4
        tokens_out = len(response.text) // 4
        costo = ((tokens_in / 1000) * 0.00025) + ((tokens_out / 1000) * 0.0005)

        # Evento de Logging Estructurado (Evento 3: LLM_SUCCESS)
        logger.info(
            "Llamada a Vertex AI exitosa",
            extra={
                "event_type": "LLM_CALL_SUCCESS",
                "latency_ms": latency_ms,
                "tokens_input": tokens_in,
                "tokens_output": tokens_out,
                "estimated_cost_usd": round(costo, 6)
            }
        )
        return response.text

    except Exception as e:
        # Si el circuito está abierto o falla Vertex AI, cae aquí
        logger.error(
            "Fallo en llamada a Vertex AI",
            extra={
                "event_type": "LLM_CALL_FAILED",
                "error": str(e),
                "circuit_state": llm_circuit_breaker.current_state
            }
        )
        # Fallback: Retornar un JSON de error controlado para que el pipeline no muera
        return '{"error": "Servicio LLM temporalmente no disponible"}'

def calcular_costo_estimado(tokens_entrada: int, tokens_salida: int) -> dict:
    """Calcula el costo estimado de la llamada al LLM."""
    total = ((tokens_entrada / 1000) * 0.00025) + ((tokens_salida / 1000) * 0.0005)
    return {"costo_total_usd": total}