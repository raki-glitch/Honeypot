FROM python:3.10
WORKDIR /app

# Install dependencies
RUN pip install fastapi torch transformers uvicorn

COPY api.py /app/api.py
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
