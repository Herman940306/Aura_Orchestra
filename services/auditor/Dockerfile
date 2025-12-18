FROM python:3.11-slim
WORKDIR /app
RUN pip install requests asyncpg
COPY services/auditor /app/services/auditor
ENV PYTHONPATH=/app
CMD ["python", "services/auditor/watch.py"]
