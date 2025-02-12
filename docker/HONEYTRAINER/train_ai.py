from kafka import KafkaConsumer
import json
import torch
from transformers import LlamaForCausalLM, LlamaTokenizer

# Load LLaMA model
model_name = "meta-llama/Llama-2-7b-chat-hf"
tokenizer = LlamaTokenizer.from_pretrained(model_name)
model = LlamaForCausalLM.from_pretrained(model_name)

# Connect to Kafka
consumer = KafkaConsumer("tpot_logs", bootstrap_servers="kafka:9092")

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
    
    # Save updated model
    model.save_pretrained("./fine_tuned_llama")
    tokenizer.save_pretrained("./fine_tuned_llama")
