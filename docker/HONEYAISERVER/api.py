from fastapi import FastAPI
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging
app = FastAPI()

# Load the latest fine-tuned model
model_name = "./fine_tuned_llama"
logging.basicConfig(level=logging.DEBUG)

try: #hi im the model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
except Exception as e:
    logging.error(f"Failed to load model {model_name}: {str(e)}")

def format_attack_log(log):
    """
    Convert attack logs dynamically to structured text.
    """
    return "\n".join([f"{key}: {value}" for key, value in log.items()])

@app.post("/predict/")
def predict(log: dict):
    attack_info = format_attack_log(log)

    inputs = tokenizer(attack_info, return_tensors="pt")
    output = model.generate(**inputs)
    
    return {"classification": tokenizer.decode(output[0], skip_special_tokens=True)}
