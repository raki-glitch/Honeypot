FROM python:3.10
WORKDIR /app

# Install dependencies
RUN pip install torch==2.6.0 transformers sentencepiece kafka-python pandas huggingface-hub

# Set the Hugging Face token as an environment variable
ENV HUGGINGFACE_TOKEN=x
#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
# Log in to Hugging Face
RUN huggingface-cli login --token $HUGGINGFACE_TOKEN

# Copy the training script into the container
COPY ./train_ai.py .

# Define the command to run the script
ENTRYPOINT ["python", "train_ai.py"]
