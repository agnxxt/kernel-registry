from typing import Dict, Any
import json
import os

# Optional import for prod
try:
    from confluent_kafka import Producer
except ImportError:
    confluent_kafka = None

class EventBus:
    """
    The asynchronous nervous system of the kernel.
    Handles 'Gossip' and high-frequency telemetry via Redpanda.
    """
    def __init__(self):
        bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
        conf = {'bootstrap.servers': bootstrap_servers}
        
        try:
            self.producer = Producer(conf) if 'Producer' in globals() else None
        except Exception:
            self.producer = None

    def publish(self, topic: str, payload: Dict[str, Any]):
        """
        Publishes a message to the bus.
        """
        if self.producer:
            try:
                self.producer.produce(topic, json.dumps(payload).encode('utf-8'))
                self.producer.flush()
            except Exception as e:
                print(f"Bus Publish Error: {e}")
        else:
            # Fallback to log for scaffolding/local-dev without Redpanda
            print(f"[BUS-MOCK] Topic: {topic} | Payload: {payload}")

