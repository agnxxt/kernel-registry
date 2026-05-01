from typing import Dict, Any, List, Optional, Callable
import json
import os

# Optional import for prod
try:
    from confluent_kafka import Producer, Consumer, KafkaError
except ImportError:
    Producer = None
    Consumer = None
    KafkaError = None

class EventBus:
    """
    The asynchronous nervous system of the kernel.
    Handles 'Gossip' and high-frequency telemetry via Redpanda.
    """
    def __init__(self, group_id: str = "kernel-group"):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
        self.group_id = group_id
        
        # 1. Initialize Producer
        try:
            self.producer = Producer({'bootstrap.servers': self.bootstrap_servers}) if Producer else None
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
            print(f"[BUS-MOCK] Topic: {topic} | Payload: {payload}")

    def listen(self, topics: List[str], callback: Callable[[str, Dict[str, Any]], None]):
        """
        Continuous listening loop for specific topics.
        """
        if not Consumer:
            print("[BUS-MOCK] Consumer not available. Skipping listen.")
            return

        conf = {
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': self.group_id,
            'auto.offset.reset': 'earliest'
        }

        consumer = Consumer(conf)
        consumer.subscribe(topics)

        print(f"Bus Listener Started: {topics} (Group: {self.group_id})")
        try:
            while True:
                msg = consumer.poll(1.0)
                if msg is None: continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF: continue
                    else:
                        print(f"Bus Read Error: {msg.error()}")
                        break

                topic = msg.topic()
                payload = json.loads(msg.value().decode('utf-8'))
                callback(topic, payload)
        finally:
            consumer.close()

