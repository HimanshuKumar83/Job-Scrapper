from app.ingestion.circuit_breaker import CircuitBreaker, CircuitState


def test_circuit_breaker_reaches_degraded():
    breaker = CircuitBreaker(failure_threshold=2, cooldown_seconds=0)
    breaker.record_failure()
    breaker.record_failure()
    assert breaker.state == CircuitState.DEGRADED


def test_circuit_breaker_half_open_recovers():
    breaker = CircuitBreaker(failure_threshold=1, cooldown_seconds=0)
    breaker.record_failure()
    breaker.state = CircuitState.HALF_OPEN
    breaker.on_half_open_result(True)
    assert breaker.state == CircuitState.HEALTHY
