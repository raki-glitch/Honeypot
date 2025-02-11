from kafka import KafkaConsumer
import json
import torch
from transformers import LlamaForCausalLM, LlamaTokenizer

# Load LLaMA Model
model_name = "meta-llama/Llama-2-7b-chat-hf"
tokenizer = LlamaTokenizer.from_pretrained(model_name)
model = LlamaForCausalLM.from_pretrained(model_name)

# Kafka Consumer
consumer = KafkaConsumer("tpot_logs", bootstrap_servers="kafka:9092")

for message in consumer:
    log = json.loads(message.value.decode("utf-8"))

    # Extract attack parameters
    attack_info = f"""
    Timestamp: {log.get('timestamp', 'Unknown')}
    Source IP: {log.get('src_ip', 'Unknown')} (Country: {log.get('geo', {}).get('country_name', 'Unknown')})
    Destination IP: {log.get('dest_ip', 'Unknown')}
    Attack Type: {log.get('attack_type', 'Unknown')}
    Protocol: {log.get('protocol', 'Unknown')}
    Ports: {log.get('src_port', 'Unknown')} → {log.get('dest_port', 'Unknown')}
    Payload: {log.get('payload', 'N/A')}
    Alert: {log.get('alert', 'None')}
    """

    inputs = tokenizer(attack_info, return_tensors="pt")

    # Perform incremental training
    outputs = model.generate(**inputs)
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))
