"""Pydantic schemas for slots API."""

from datetime import datetime

from pydantic import BaseModel, Field


class SlotResponse(BaseModel):
    """Response model for a single slot."""

    office_name: str = Field(..., description="Office name")
    office_address: str = Field(..., description="Office address")
    date: str = Field(..., description="Date in DD/MM/YYYY format")
    time: str = Field(..., description="Time in HH:MM format")
    datetime_iso: str = Field(..., description="ISO 8601 datetime (YYYY-MM-DDTHH:MM:SS)")
    office_id: str = Field(default="", description="Office ID if available")


class SlotListResponse(BaseModel):
    """Response model for list of slots."""

    slots: list[SlotResponse] = Field(..., description="List of available slots")
    count: int = Field(..., description="Number of slots")
    procedure_id: str = Field(..., description="Procedure ID queried")
    region_id: str = Field(..., description="Region ID queried")
    scraped_at: datetime = Field(..., description="Timestamp of scraping")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    code: int = Field(..., description="HTTP status code")
