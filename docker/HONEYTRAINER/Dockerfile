FROM python:3.10
WORKDIR /app

# Install dependencies
RUN pip install torch==2.6.0 transformers kafka-python pandas

COPY ./train_ai.py /app/train_ai.py
CMD ["chmod","+x","/app/train_ai.py"]

ENTRYPOINT  ["python", "/app/train_ai.py"]
