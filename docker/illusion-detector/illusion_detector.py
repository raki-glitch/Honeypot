from kafka import KafkaConsumer, KafkaProducer
import json
import time
import re
import os
kafka_broker = os.getenv("KAFKA_BROKER", "127.0.0.1:9092")  # Default to "kafka:9092" if not set

INPUT_TOPIC = "tpot_logs"
OUTPUT_TOPIC = "illusion_alerts"

# Set up Kafka consumer
consumer = KafkaConsumer(INPUT_TOPIC, bootstrap_servers=kafka_broker, value_deserializer=lambda m: json.loads(m.decode('utf-8')))
producer = KafkaProducer(bootstrap_servers=kafka_broker, value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# Illusion attack detection patterns
DECEPTION_PATTERNS = [
    r"(modifying logs|log deletion detected)",
    r"(delayed execution|long sleep detected)",
    r"(anti-analysis detected|debugger presence)",
    r"(process injection|code injection)",
]

def detect_illusion_attacks(log):
    for pattern in DECEPTION_PATTERNS:
        if re.search(pattern, log.get("message", ""), re.IGNORECASE):
            return True
    return False

# Monitor honeypot logs
for message in consumer:
    log_data = message.value

    if detect_illusion_attacks(log_data):
        print(f"[ALERT] Illusion attack detected: {log_data}")
        producer.send(OUTPUT_TOPIC, log_data)
