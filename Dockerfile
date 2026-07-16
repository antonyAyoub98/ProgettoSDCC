FROM python:3.10-slim

ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY config/requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 --retries=5 -r requirements.txt
COPY . .
EXPOSE 8080

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]