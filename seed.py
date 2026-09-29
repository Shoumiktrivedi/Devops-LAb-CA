"""Load demo data:  python seed.py          (only if DB is empty)
                   python seed.py --reset  (wipe and reload)"""
import sys

from app import create_app
from app.services import seed_demo_data

if __name__ == "__main__":
    with create_app().app_context():
        n = seed_demo_data(reset="--reset" in sys.argv)
        print(f"Added {n} demo transactions" if n else "Database already has data (use --reset to replace)")
