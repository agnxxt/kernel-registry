import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

def setup_telemetry(service_name: str):
    """
    Initializes OpenTelemetry tracing for the kernel.
    """
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    
    # OTLP Exporter (sending to Jaeger)
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4317")
    otlp_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
    
    span_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)
    
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)

tracer = trace.get_tracer("agent-kernel")
