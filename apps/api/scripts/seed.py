"""Seed database from fixture collectors."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.database import SessionLocal, init_db  # noqa: E402
from app.pipeline import run_pipeline  # noqa: E402


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        results = run_pipeline(db)
        for row in results:
            print(
                f"[{row['status']}] {row['source']}: "
                f"collected={row['jobs_collected']} created={row['jobs_created']} "
                f"skipped={row['jobs_skipped']}"
            )
    finally:
        db.close()


if __name__ == "__main__":
    main()
