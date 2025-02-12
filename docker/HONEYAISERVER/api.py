from fastapi import FastAPI
from transformers import LlamaForCausalLM, LlamaTokenizer

app = FastAPI()

# Load the latest fine-tuned model
model_name = "./fine_tuned_llama"
tokenizer = LlamaTokenizer.from_pretrained(model_name)
model = LlamaForCausalLM.from_pretrained(model_name)

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
