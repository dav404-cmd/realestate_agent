import pytest
from pathlib import Path

def main():
    root = Path(__file__).parent
    exit_code = pytest.main([
        str(root / "scraper_test.py"),
        str(root / "db_test_v1.py"),
        "-v"
    ])
    raise SystemExit(exit_code)

if __name__ == "__main__":
    main()