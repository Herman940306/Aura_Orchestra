import os
import psycopg
from datetime import datetime, timezone


class Ledger:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")

    def record(self, model_name, job_id, score, penalties, severity):
        try:
            with psycopg.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO model_performance
                        (model_name, job_id, score, penalties, error_severity, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                        (
                            model_name,
                            job_id,
                            score,
                            penalties,
                            severity,
                            datetime.now(timezone.utc),
                        ),
                    )
        except Exception as e:
            print(f"Ledger error: {e}")

    def get_history(self, model_name, limit=10):
        try:
            with psycopg.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT score, penalties, error_severity, created_at
                        FROM model_performance
                        WHERE model_name = %s
                        ORDER BY created_at DESC
                        LIMIT %s
                    """,
                        (model_name, limit),
                    )
                    return cur.fetchall()
        except Exception:
            return []
