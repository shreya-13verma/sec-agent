"""Test verifying strict constraint of 0 JSON/JSONB columns in DB schema."""
import pytest
from sqlalchemy import inspect
from backend.app.core.database import Base
import backend.app.models  # load all models

def test_strictly_zero_json_columns():
    """Verify that no table in Base metadata has JSON or JSONB column types."""
    tables = Base.metadata.tables

    assert len(tables) >= 6

    json_column_findings = []
    for table_name, table in tables.items():
        for column in table.columns:
            col_type = str(column.type).upper()
            if "JSON" in col_type or "BLOB" in col_type:
                json_column_findings.append(f"{table_name}.{column.name} ({col_type})")

    assert len(json_column_findings) == 0, f"Found JSON columns violating constraint: {json_column_findings}"
