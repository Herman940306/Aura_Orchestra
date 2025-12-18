FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
# We need psycopg (binary) for synchronous DB access in Accountant
RUN pip install fastapi uvicorn "psycopg[binary]" pydantic requests
COPY *.py /app/
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
