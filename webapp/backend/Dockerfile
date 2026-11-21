FROM python:3.10-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY webapp/backend/requirements.txt /workspace/webapp/backend/requirements.txt
RUN pip install --no-cache-dir -r /workspace/webapp/backend/requirements.txt

COPY serve /workspace/serve
COPY research /workspace/research
COPY webapp/backend /workspace/webapp/backend

WORKDIR /workspace/webapp/backend
ENV PYTHONPATH=/workspace

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
