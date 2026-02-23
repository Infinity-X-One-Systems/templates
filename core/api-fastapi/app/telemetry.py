"""OpenTelemetry instrumentation hooks."""
from __future__ import annotations

import os
from typing import Optional


def init_telemetry(service_name: str, env: str, endpoint: Optional[str] = None) -> None:
    """Initialise OTEL tracing if an endpoint is configured."""
    otlp_endpoint = endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    if not otlp_endpoint:
        return  # No-op in local dev without a collector

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create(
            {"service.name": service_name, "deployment.environment": env}
        )
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        FastAPIInstrumentor().instrument()
    except ImportError:
        pass  # OTEL packages not installed — skip silently
