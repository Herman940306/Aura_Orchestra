FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn asyncpg pyyaml
COPY services/router/capabilities.yaml /app/capabilities.yaml
COPY services/router/router.py /app/router.py
CMD ["uvicorn", "router:app", "--host", "0.0.0.0", "--port", "8000"]
