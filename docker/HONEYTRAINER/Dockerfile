FROM python:3.10
WORKDIR /app

# Install dependencies
RUN pip install torch==2.6.0 transformers kafka-python pandas

COPY ./train_ai.py .
RUN ls -la /app
ENTRYPOINT ["python", "train_ai.py"]
