import pybreaker
import logging

logger = logging.getLogger("app.resilience")

# Configuración del Circuit Breaker:
# fail_max: Se abre el circuito tras 3 fallos consecutivos.
# reset_timeout: Intenta cerrarse (medio abierto) después de 30 segundos.
llm_circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=30,
    name="VertexAI_Circuit"
)

# Listener para auditar cuándo se abre o cierra el circuito (Audit Trail)
class CircuitBreakerListener(pybreaker.CircuitBreakerListener):
    def state_change(self, cb, old_state, new_state):
        logger.warning(
            f"Circuit Breaker '{cb.name}' cambió de estado: {old_state.name} -> {new_state.name}",
            extra={"event_type": "CIRCUIT_BREAKER_STATE_CHANGE", "state": new_state.name}
        )

llm_circuit_breaker.add_listener(CircuitBreakerListener())