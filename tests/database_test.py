import pytest
import pandas as pd
from sqlalchemy import text


from manage_db.db_manager import DbManager

@pytest.fixture
def db():
    db_logic = DbManager("jp_realestate")
    yield db_logic
    db_logic.close_conn()

def test_conn(db):
    assert db.conn is not None
    assert db.cursor is not None


def test_engine_connectivity(db):
    engine = db.get_db_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

def test_data(db):
    df = db.load_data()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

def test_data_columns(db):
    df = db.load_data()
    expected_cols = {"id", "source", "scraped_at"}
    assert expected_cols.issubset(df.columns)