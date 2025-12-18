FROM python:3.11-slim
WORKDIR /app
RUN pip install requests asyncpg
COPY services/validator /app/services/validator
# validator might need shared modules if we structured it that way, 
# but for now scoring.py is standalone-ish.
# We need a main loop for validator? 
# Batch 4 text says: "Validator picks job up... and runs scoring".
# It doesn't explicitly give validator/main.py code, only validator/scoring.py.
# I need to create a simple main loop that listens for validation requests or polls.
# "Validator picks job up (via Manager notifying or by polling SUBMITTED status)"
# I will implement a polling main.py for it.

COPY services/validator/main.py /app/main.py
ENV PYTHONPATH=/app
CMD ["python", "main.py"]
