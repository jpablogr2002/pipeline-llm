from google.adk.agents import LlmAgent
from app.agent.tools import analizar_con_llm, calcular_costo_estimado

root_agent = LlmAgent(
    name="MediaGroupAnalyzer",
    model="gemini-3.5-flash",
    description="Agente experto en analizar artículos periodísticos.",
    instruction="Eres un asistente de MediaGroup LATAM. Usa 'analizar_con_llm' para procesar el artículo y responder en JSON.",
    tools=[analizar_con_llm, calcular_costo_estimado]
)