"""Slots API router."""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from src.schemas.slots import SlotListResponse, SlotResponse
from src.services.settings import Settings, get_settings
from src.services.srcei.client import SRCEIPlaywrightClient
from src.services.srcei.config import SRCEIConfig
from src.services.srcei.recommender import format_slot_datetime_iso, sort_slots_by_datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/slots", tags=["slots"])


@router.get("", response_model=SlotListResponse)
async def get_slots(
    procedure_id: str = Query(
        ...,
        pattern="^(6|9|10|11|12|13|14|15)$",
        description="Procedure ID (6=Renovación, 9=Reimpresión, 10=Extranjero, 11=Pasaporte, 12=Menores, 13=Apostilla, 14=Rectificaciones, 15=Vehículos)",
    ),
    region_id: str = Query(
        ...,
        pattern="^(1[0-6]|[1-9])$",
        description="Region ID (1-16)",
    ),
    settings: Settings = Depends(get_settings),
) -> SlotListResponse:
    """
    Get available appointment slots for a procedure and region.

    This endpoint performs real-time scraping using Playwright, so response times
    will be 10-30 seconds. Slots are sorted by datetime (earliest first).

    Args:
        procedure_id: Procedure type ID (6-15)
        region_id: Chilean region ID (1-16)
        settings: Application settings (injected)

    Returns:
        List of available slots sorted by datetime

    Raises:
        HTTPException: 400 for validation errors, 503 for service unavailable, 504 for timeout
    """
    logger.info(f"Fetching slots for procedure={procedure_id}, region={region_id}")

    try:
        # Create SRCEI config from settings
        config = SRCEIConfig(
            rut=settings.srcei_rut,
            password=settings.srcei_password,
        )

        # Initialize Playwright client and get slots
        async with SRCEIPlaywrightClient(config, headless=True) as client:
            # Login
            if not await client.login():
                logger.error("Login failed")
                raise HTTPException(status_code=503, detail="Failed to authenticate with SRCEI")

            # Get slots
            raw_slots = await client.get_slots_by_region(procedure_id, region_id)

            if not raw_slots:
                logger.info("No slots found")
                return SlotListResponse(
                    slots=[],
                    count=0,
                    procedure_id=procedure_id,
                    region_id=region_id,
                    scraped_at=datetime.utcnow(),
                )

            # Sort slots by datetime
            sorted_slots = sort_slots_by_datetime(raw_slots)

            # Convert to response format
            slot_responses = [
                SlotResponse(
                    office_name=slot["nombreOficina"],
                    office_address=slot["direccionOficina"],
                    date=slot["fechaDisponible"],
                    time=slot["horaDisponible"],
                    datetime_iso=format_slot_datetime_iso(slot),
                    office_id=slot.get("idOficina", ""),
                )
                for slot in sorted_slots
            ]

            logger.info(f"Successfully retrieved {len(slot_responses)} slots")

            return SlotListResponse(
                slots=slot_responses,
                count=len(slot_responses),
                procedure_id=procedure_id,
                region_id=region_id,
                scraped_at=datetime.utcnow(),
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching slots: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
