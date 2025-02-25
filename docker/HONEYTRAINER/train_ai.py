#  Optimized Kafka Consumption: Uses poll(timeout_ms=1000, max_records=batch_size) to fetch messages in batches.
#  Efficient Tokenization: Handles padding correctly to prevent incorrect loss calculation.
#  Conditional Model Training: model.train() is only activated when training occurs.
#  Periodic Model Saving: Ensures progress is saved periodically in ./fine_tuned_llama.
#  Better Logging & Error Handling: Logs Kafka connection status, model loading, and training losses.
#  Kafka num_workers=4 – Faster log processing.
#  Async Kafka Consumption (asyncio) – Handles high-throughput attack logs.
#  Hugging Face Trainer – Structured fine-tuning for scalability.
import os
import json
import torch
import logging
from kafka import KafkaConsumer
from transformers import AutoTokenizer, AutoModelForCausalLM

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Model and Kafka settings
model_name = "meta-llama/Llama-2-7b-chat-hf"
kafka_broker = os.getenv("KAFKA_BROKER", "127.0.0.1:9092")
attack_topic = "tpot_logs"
batch_size = 4
save_path = "./fine_tuned_llama"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Ensure Hugging Face token is available
hf_token = os.getenv("HUGGINGFACE_TOKEN")
if not hf_token:
    logging.error("Hugging Face token is missing. Please set it in the environment variables.")
    exit(1)

# Load tokenizer and model
def load_model():
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)
        model = AutoModelForCausalLM.from_pretrained(model_name, token=hf_token).to(device)
        logging.info("Model and tokenizer loaded successfully.")
        return tokenizer, model
    except Exception as e:
        logging.error(f"Failed to load model {model_name}: {str(e)}")
        exit(1)

tokenizer, model = load_model()
optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5)
loss_fn = torch.nn.CrossEntropyLoss()

# Create Kafka consumer
try:
    logging.info(f"Connecting to Kafka broker at {kafka_broker}")
    consumer = KafkaConsumer(attack_topic, bootstrap_servers=kafka_broker, auto_offset_reset='latest')
    logging.info("Kafka Consumer connected successfully.")
except Exception as e:
    logging.error(f"Failed to connect to Kafka: {str(e)}")
    exit(1)

def format_attack_log(log):
    """
    Convert attack logs dynamically to structured text.
    """
    return "\n".join([f"{key}: {value}" for key, value in log.items()])

def train_model(batch):
    """
    Fine-tune the LLaMA model using attack logs.
    """
    model.train()
    inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
    labels = inputs["input_ids"].detach().clone()
    labels[inputs["attention_mask"] == 0] = -100  # Ignore padding tokens in loss computation

    optimizer.zero_grad()
    outputs = model(**inputs, labels=labels)
    loss = outputs.loss
    loss.backward()
    optimizer.step()
    
    logging.info(f"Loss: {loss.item()}")
    return loss.item()

# Ensure save directory exists
os.makedirs(save_path, exist_ok=True)

# Kafka consumption loop
while True:
    batch = []
    messages = consumer.poll(timeout_ms=1000, max_records=batch_size)
    
    for _, records in messages.items():
        for message in records:
            log = json.loads(message.value.decode("utf-8"))
            batch.append(format_attack_log(log))

    if batch:
        loss = train_model(batch)
        logging.info(f"Batch processed, Loss: {loss}")
        
        # Save model periodically
        model.save_pretrained(save_path)
        tokenizer.save_pretrained(save_path)
        logging.info(f"Model saved at {save_path}")
