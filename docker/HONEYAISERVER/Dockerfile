FROM python:3.10
WORKDIR /app

# Install dependencies
RUN pip install fastapi torch transformers uvicorn sentencepiece pandas huggingface-hub

# Set the Hugging Face token as an environment variable
ENV HUGGINGFACE_TOKEN=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

# Log in to Hugging Face
RUN huggingface-cli login --token $HUGGINGFACE_TOKEN

COPY api.py /app/api.py
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
