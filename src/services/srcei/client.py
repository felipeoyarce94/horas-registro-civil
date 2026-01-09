"""SRCEI Playwright client for slot scraping (async)."""

import asyncio
import logging
from typing import Optional

from playwright.async_api import Page, Browser, BrowserContext, async_playwright

from .config import SRCEIConfig

logger = logging.getLogger(__name__)


class SRCEIPlaywrightClient:
    """
    Async Playwright-based client for SRCEI appointment system.

    Uses a real browser to avoid WAF/bot detection.
    """

    BASE_URL = "https://solicitudeswebrc.srcei.cl/ReservaDeHoraSRCEI"

    def __init__(self, config: SRCEIConfig, headless: bool = True):
        """
        Initialize SRCEI Playwright client.

        Args:
            config: SRCEIConfig instance with credentials
            headless: Run browser in headless mode
        """
        self.config = config
        self.config.validate()
        self.headless = headless

        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_authenticated = False

    async def start_browser(self) -> None:
        """Start the Playwright browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        self.page = await self.context.new_page()

        # Add stealth settings
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)

    async def close(self) -> None:
        """Close the browser and cleanup."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def login(self) -> bool:
        """
        Authenticate with SRCEI using ClaveÚnica credentials.

        Returns:
            True if login successful, False otherwise
        """
        if not self.page:
            await self.start_browser()

        try:
            logger.info("Navigating to login page...")
            await self.page.goto(f"{self.BASE_URL}/web/init.srcei", wait_until="networkidle")
            await asyncio.sleep(1)

            # Check if WAF blocked
            title = await self.page.title()
            if "Request Rejected" in title:
                logger.error("WAF blocked access")
                return False

            # Wait for login form
            logger.info(f"Logging in as: {self.config.rut}")
            await self.page.wait_for_selector('input[name="run"]', timeout=10000)

            # Fill credentials
            await self.page.fill('input[name="run"]', self.config.rut)
            await self.page.fill('input[name="pass"]', self.config.password)

            # Click login button
            await self.page.click('button[type="submit"], input[type="submit"], .btn-primary')

            # Wait for navigation
            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)

            # Check if login successful
            current_url = self.page.url
            title = await self.page.title()

            if "seleccion" in current_url.lower() or "Reserva de Hora" in title:
                self.is_authenticated = True
                logger.info("Login successful")
                return True
            else:
                logger.error(f"Login failed. Current page: {title}")
                return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    async def select_procedure(self, procedure_id: str) -> bool:
        """
        Select a procedure from the selection page.

        Args:
            procedure_id: Procedure type ID (6-15)

        Returns:
            True if selection successful
        """
        if not self.is_authenticated:
            raise ValueError("Must login first")

        procedure_map = {
            "6": "Renovación Chileno/a",
            "9": "Reimpresión cédula",
            "10": "Renovación Extranjero/a",
            "11": "Solicitud de Pasaporte",
            "12": "Menores de Edad",
            "13": "Apostilla",
            "14": "Rectificaciones",
            "15": "Vehículos",
        }

        procedure_name = procedure_map.get(procedure_id, procedure_id)
        logger.info(f"Selecting procedure: {procedure_name}")

        try:
            # Try different selectors
            selectors = [
                f'button:has-text("{procedure_name}")',
                f'text="{procedure_name}"',
                f'button:text-is("{procedure_name}")',
            ]

            clicked = False
            for selector in selectors:
                try:
                    await self.page.click(selector, timeout=3000)
                    clicked = True
                    break
                except Exception:
                    continue

            if not clicked:
                # Try clicking by button text match
                buttons = await self.page.query_selector_all("button.btn")
                for btn in buttons:
                    text = await btn.inner_text()
                    if procedure_name.split()[0] in text:
                        await btn.click()
                        clicked = True
                        break

            if clicked:
                await self.page.wait_for_load_state("networkidle")
                await asyncio.sleep(1)
                logger.info("Procedure selected")
                return True
            else:
                logger.error("Could not find procedure button")
                return False

        except Exception as e:
            logger.error(f"Error selecting procedure: {e}")
            return False

    async def select_region(self, region_id: str) -> bool:
        """
        Select a region from the dropdown.

        Args:
            region_id: Region ID (1-16)

        Returns:
            True if selection successful
        """
        logger.info(f"Selecting region ID: {region_id}")

        try:
            await asyncio.sleep(1)

            # Try multiple selectors for the dropdown
            selectors = [
                "select",
                'select[name="idRegion"]',
                "select#idRegion",
                "select.form-control",
            ]

            selected = False
            for selector in selectors:
                try:
                    select_elem = await self.page.query_selector(selector)
                    if select_elem:
                        await self.page.select_option(selector, region_id)
                        selected = True
                        logger.info(f"Selected region: {region_id}")
                        break
                except Exception:
                    continue

            if not selected:
                logger.error("Could not find region dropdown")
                return False

            # Wait for page to react
            await asyncio.sleep(1)
            await self.page.wait_for_load_state("networkidle")

            return True

        except Exception as e:
            logger.error(f"Error selecting region: {e}")
            return False

    async def get_slots_by_region(self, procedure_id: str, region_id: str) -> list[dict]:
        """
        Get available appointment slots for a region.

        Args:
            procedure_id: Procedure type ID
            region_id: Region ID

        Returns:
            List of slot dictionaries
        """
        if not self.is_authenticated:
            raise ValueError("Must login first")

        # Select procedure
        if not await self.select_procedure(procedure_id):
            return []

        # Select region
        if not await self.select_region(region_id):
            return []

        logger.info("Fetching available slots...")

        try:
            # Wait for slots to load
            await asyncio.sleep(2)

            # Extract slots using JavaScript
            slots_data = await self.page.evaluate("""
                () => {
                    const slots = [];

                    const cards = document.querySelectorAll('.card, [class*="card"], .col-md-6 > div, .col-lg-4 > div');

                    cards.forEach(card => {
                        const text = card.innerText || '';

                        if (!text.includes('Agendar')) return;

                        const lines = text.split('\\n').map(t => t.trim()).filter(t => t);

                        let officeName = '';
                        let address = '';
                        let day = '';
                        let month = '';
                        let time = '';

                        if (lines.length > 0) officeName = lines[0];
                        if (lines.length > 1) address = lines[1];

                        const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                                          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];

                        for (const line of lines) {
                            if (/^\\d{1,2}$/.test(line) && parseInt(line) >= 1 && parseInt(line) <= 31) {
                                day = line;
                            }
                            if (monthNames.some(m => line.toLowerCase() === m.toLowerCase())) {
                                month = line;
                            }
                            if (/^\\d{1,2}:\\d{2}$/.test(line)) {
                                time = line;
                            }
                        }

                        if (officeName && day && month) {
                            const monthMap = {
                                'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
                                'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
                                'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
                            };

                            const dayPadded = day.padStart(2, '0');
                            const monthNum = monthMap[month.toLowerCase()] || '01';
                            const year = new Date().getFullYear();

                            slots.push({
                                nombreOficina: officeName,
                                direccionOficina: address,
                                fechaDisponible: `${dayPadded}/${monthNum}/${year}`,
                                horaDisponible: time || '00:00',
                                idOficina: ''
                            });
                        }
                    });

                    return slots;
                }
            """)

            # Remove duplicates
            seen = set()
            unique_slots = []
            for slot in slots_data:
                key = f"{slot['nombreOficina']}_{slot['fechaDisponible']}_{slot['horaDisponible']}"
                if key not in seen:
                    seen.add(key)
                    unique_slots.append(slot)

            logger.info(f"Found {len(unique_slots)} unique slots")
            return unique_slots

        except Exception as e:
            logger.error(f"Error fetching slots: {e}")
            return []
