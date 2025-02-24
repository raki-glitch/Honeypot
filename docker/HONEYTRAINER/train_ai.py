from kafka import KafkaConsumer
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
import logging
# Load LLaMA model
model_name = "meta-llama/Llama-2-7b-chat-hf"

logging.basicConfig(level=logging.DEBUG)
try: #hi im the model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
except Exception as e:
    logging.error(f"Failed to load model {model_name}: {str(e)}")

kafka_broker = os.getenv("KAFKA_BROKER", "127.0.0.1:9092")  # Default to "kafka:9092" if not set
# Connect to Kafka
consumer = KafkaConsumer("tpot_logs", bootstrap_servers=kafka_broker)

def format_attack_log(log):
    """
    Convert attack logs dynamically to structured text.
    """
    return "\n".join([f"{key}: {value}" for key, value in log.items()])

for message in consumer:
    log = json.loads(message.value.decode("utf-8"))
    attack_text = format_attack_log(log)

    inputs = tokenizer(attack_text, return_tensors="pt")
    
    # Fine-tune LLaMA dynamically
    outputs = model(**inputs)
    save_path = "./fine_tuned_llama"

    # If a file exists instead of a directory, remove it
    if os.path.exists(save_path) and not os.path.isdir(save_path):
        os.remove(save_path)  # Delete the file
        os.makedirs(save_path)  # Create a proper directory

    # Save model and tokenizer
    model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)
    print(f"Model is being saved at: {save_path}")
