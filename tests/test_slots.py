"""Tests for slots API."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.services.srcei.recommender import (
    format_slot_datetime,
    format_slot_datetime_iso,
    parse_slot_date,
    sort_slots_by_datetime,
)

client = TestClient(app)


def test_read_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "horas-registro-civil API"
    assert data["status"] == "healthy"


def test_get_slots_missing_params():
    """Test slots endpoint with missing parameters."""
    response = client.get("/slots")
    assert response.status_code == 422  # Validation error


def test_get_slots_invalid_procedure():
    """Test slots endpoint with invalid procedure_id."""
    response = client.get("/slots?procedure_id=99&region_id=13")
    assert response.status_code == 422  # Validation error


def test_get_slots_invalid_region():
    """Test slots endpoint with invalid region_id."""
    response = client.get("/slots?procedure_id=6&region_id=99")
    assert response.status_code == 422  # Validation error


def test_parse_slot_date():
    """Test date parsing."""
    assert parse_slot_date("29/01/2026") == "2026-01-29"
    assert parse_slot_date("01/12/2025") == "2025-12-01"
    assert parse_slot_date("5/3/2026") == "2026-03-05"


def test_format_slot_datetime():
    """Test datetime formatting for sorting."""
    slot = {"fechaDisponible": "29/01/2026", "horaDisponible": "09:30"}
    assert format_slot_datetime(slot) == "2026-01-29 09:30"


def test_format_slot_datetime_iso():
    """Test ISO datetime formatting."""
    slot = {"fechaDisponible": "29/01/2026", "horaDisponible": "09:30"}
    assert format_slot_datetime_iso(slot) == "2026-01-29T09:30:00"


def test_sort_slots_by_datetime():
    """Test slot sorting."""
    slots = [
        {"fechaDisponible": "30/01/2026", "horaDisponible": "10:00", "nombreOficina": "B"},
        {"fechaDisponible": "29/01/2026", "horaDisponible": "15:00", "nombreOficina": "A"},
        {"fechaDisponible": "29/01/2026", "horaDisponible": "09:30", "nombreOficina": "C"},
    ]
    sorted_slots = sort_slots_by_datetime(slots)
    assert sorted_slots[0]["nombreOficina"] == "C"  # 29/01 09:30
    assert sorted_slots[1]["nombreOficina"] == "A"  # 29/01 15:00
    assert sorted_slots[2]["nombreOficina"] == "B"  # 30/01 10:00


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_slots_integration():
    """
    Integration test for slots endpoint.

    This test requires valid SRCEI credentials in environment variables.
    Run with: pytest tests/ -v -m integration
    """
    pytest.skip("Integration test - requires valid SRCEI credentials")

    response = client.get("/slots?procedure_id=6&region_id=13")
    assert response.status_code == 200

    data = response.json()
    assert "slots" in data
    assert "count" in data
    assert data["procedure_id"] == "6"
    assert data["region_id"] == "13"
    assert isinstance(data["slots"], list)
