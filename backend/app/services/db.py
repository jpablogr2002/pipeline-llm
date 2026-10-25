from google.cloud import firestore
import os
import logging

logger = logging.getLogger(__name__)

db = firestore.Client(project=os.getenv("GCP_PROJECT_ID"))

def guardar_analisis(task_id: str, data: dict):
    try:
        db.collection("analisis").document(task_id).set(data)
    except Exception as e:
        logger.error(f"Error guardando en Firestore: {e}")

def obtener_historial(limite=5):
    try:
        # Ordenamos por timestamp descendente
        docs = db.collection("analisis").order_by(
            "timestamp", direction=firestore.Query.DESCENDING
        ).limit(limite).stream()
        
        historial = []
        for doc in docs:
            data = doc.to_dict()
            # Formateamos el timestamp para que el frontend lo muestre bonito
            if "timestamp" in data:
                import datetime
                data["timestamp"] = datetime.datetime.fromtimestamp(data["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            historial.append(data)
        return historial
    except Exception as e:
        logger.error(f"Error leyendo Firestore: {e}")
        return []

def calcular_metricas():
    try:
        # Traemos todos los documentos para calcular las métricas
        docs = list(db.collection("analisis").stream())
        total = len(docs)
        
        if total == 0:
            return {"total_procesados": 0, "latencia_promedio_ms": 0, "costo_estimado_usd": 0}

        latencia_total = sum(doc.to_dict().get("latency_ms", 0) for doc in docs)
        latencia_promedio = latencia_total / total
        
        # Costo estimado: Supongamos $0.0006 USD por artículo (ajústalo a tu gusto)
        costo_estimado = total * 0.0006

        return {
            "total_procesados": total,
            "latencia_promedio_ms": round(latencia_promedio, 2),
            "costo_estimado_usd": round(costo_estimado, 4)
        }
    except Exception as e:
        logger.error(f"Error calculando métricas: {e}")
        return {"total_procesados": 0, "latencia_promedio_ms": 0, "costo_estimado_usd": 0}