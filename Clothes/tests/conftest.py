import pytest
from app.data.db_store import db_store

@pytest.fixture(autouse=True)
def run_around_tests():
    # Setup: Reset the database to standard seed data before each test
    db_store.clear()
    yield
    # Teardown (optional, clear again)
    db_store.clear()
