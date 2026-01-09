"""Slot sorting and filtering utilities for SRCEI appointments."""

from datetime import datetime


def parse_slot_date(fecha_disponible: str) -> str:
    """
    Parse SRCEI date format to ISO format.

    Args:
        fecha_disponible: Date in DD/MM/YYYY format

    Returns:
        Date in YYYY-MM-DD format (ISO 8601)
    """
    day, month, year = fecha_disponible.split("/")
    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"


def format_slot_datetime(slot: dict) -> str:
    """
    Format slot date and time for sorting.

    Args:
        slot: Slot dictionary with fechaDisponible and horaDisponible

    Returns:
        Formatted datetime string (e.g., "2026-01-29 09:30")
    """
    iso_date = parse_slot_date(slot["fechaDisponible"])
    time_str = slot["horaDisponible"]
    return f"{iso_date} {time_str}"


def sort_slots_by_datetime(slots: list[dict]) -> list[dict]:
    """
    Sort slots by date and time (earliest first).

    Args:
        slots: List of slot dictionaries

    Returns:
        Sorted list of slots
    """
    return sorted(slots, key=format_slot_datetime)


def format_slot_datetime_iso(slot: dict) -> str:
    """
    Format slot date and time as ISO 8601 datetime.

    Args:
        slot: Slot dictionary with fechaDisponible and horaDisponible

    Returns:
        ISO 8601 datetime string (e.g., "2026-01-29T09:30:00")
    """
    iso_date = parse_slot_date(slot["fechaDisponible"])
    time_str = slot["horaDisponible"]
    return f"{iso_date}T{time_str}:00"
