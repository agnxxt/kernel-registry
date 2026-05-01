from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource, ValueType, PostgreSQLSource
from feast.types import Float32, Int64, String

# 1. Define the Agent Entity
agent = Entity(name="agent", join_keys=["agent_id"], description="Kernel Agent ID")

# 2. Define the Data Source (Postgres)
# Feast will pull historical cognitive metrics from this source
cognitive_source = PostgreSQLSource(
    name="cognitive_stats",
    query="SELECT agent_id, avg_latency_ms, historical_hallucination_rate, event_timestamp, created_at FROM cognitive_metrics",
    timestamp_field="event_timestamp",
    created_timestamp_column="created_at",
)

# 3. Define the Feature View
agent_cognitive_fv = FeatureView(
    name="agent_cognitive_metrics",
    entities=[agent],
    ttl=timedelta(days=1),
    schema=[
        Field(name="avg_latency_ms", dtype=Int64),
        Field(name="historical_hallucination_rate", dtype=Float32),
    ],
    online=True,
    source=cognitive_source,
    tags={"domain": "cognition"},
)
