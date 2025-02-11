FROM python:3.10
WORKDIR /app

# Install dependencies
RUN pip install torch transformers kafka-python pandas

COPY train_ai.py /app/train_ai.py
CMD ["python", "/app/train_ai.py"]
