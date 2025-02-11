from fastapi import FastAPI
from transformers import LlamaForCausalLM, LlamaTokenizer

app = FastAPI()

# Load trained LLaMA model
model_name = "./fine_tuned_llama"
tokenizer = LlamaTokenizer.from_pretrained(model_name)
model = LlamaForCausalLM.from_pretrained(model_name)

@app.post("/predict/")
def predict(log: dict):
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
    output = model.generate(**inputs)
    return {"classification": tokenizer.decode(output[0], skip_special_tokens=True)}
