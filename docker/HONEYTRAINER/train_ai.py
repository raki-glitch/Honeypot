from kafka import KafkaConsumer
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
import logging

# Load LLaMA model
model_name = "meta-llama/Llama-2-7b-chat-hf"
logging.basicConfig(level=logging.DEBUG)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model():
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
        model.train()  # Set to training mode
        return tokenizer, model
    except Exception as e:
        logging.error(f"Failed to load model {model_name}: {str(e)}")
        exit(1)

tokenizer, model = load_model()

# Kafka setup
kafka_broker = os.getenv("KAFKA_BROKER", "127.0.0.1:9092")
consumer = KafkaConsumer("tpot_logs", bootstrap_servers=kafka_broker)

# Training setup
optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5)
loss_fn = torch.nn.CrossEntropyLoss()
batch_size = 4
attack_logs = []

def format_attack_log(log):
    """
    Convert attack logs dynamically to structured text.
    """
    return "\n".join([f"{key}: {value}" for key, value in log.items()])

def train_model(batch):
    inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
    labels = inputs["input_ids"].detach().clone()
    
    optimizer.zero_grad()
    outputs = model(**inputs, labels=labels)
    loss = outputs.loss
    loss.backward()
    optimizer.step()
    
    logging.info(f"Loss: {loss.item()}")
    return loss.item()

save_path = "./fine_tuned_llama"

if os.path.exists(save_path) and not os.path.isdir(save_path):
    os.remove(save_path)
    os.makedirs(save_path)

# Kafka consumption loop
for message in consumer:
    log = json.loads(message.value.decode("utf-8"))
    attack_logs.append(format_attack_log(log))
    
    if len(attack_logs) >= batch_size:
        train_model(attack_logs)
        attack_logs = []

        # Save model periodically
        model.save_pretrained(save_path)
        tokenizer.save_pretrained(save_path)
        logging.info(f"Model saved at {save_path}")
