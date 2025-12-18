FROM python:3.11-slim
WORKDIR /app
RUN pip install asyncpg
COPY services/hr /app/services/hr
ENV PYTHONPATH=/app
CMD ["python", "services/hr/hr_worker.py"]
