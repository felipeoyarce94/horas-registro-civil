"""Configuration for SRCEI service."""

from pydantic import BaseModel, field_validator


class SRCEIConfig(BaseModel):
    """Configuration for SRCEI appointment booking client."""

    # User credentials
    rut: str  # Chilean RUT with dash (e.g., "12345678-9")
    password: str

    # Base URL for SRCEI
    base_url: str = "https://solicitudeswebrc.srcei.cl/ReservaDeHoraSRCEI"

    # HTTP client settings
    timeout: int = 30  # seconds

    @field_validator("rut")
    @classmethod
    def rut_must_contain_dash(cls, v: str) -> str:
        """Validate RUT format contains dash separator."""
        if "-" not in v:
            raise ValueError(f"RUT must contain dash separator: {v}")
        return v


class ProcedureType:
    """SRCEI procedure type IDs."""

    RENOVACION_CHILENO = "6"  # Renovación Chileno/a
    REIMPRESION_CEDULA = "9"  # Reimpresión cédula
    RENOVACION_EXTRANJERO = "10"  # Renovación Extranjero/a
    SOLICITUD_PASAPORTE = "11"  # Solicitud de Pasaporte
    MENORES_EDAD = "12"  # Menores de Edad
    APOSTILLA = "13"  # Apostilla (Máximo 5 documentos)
    RECTIFICACIONES = "14"  # Rectificaciones - Cambio Orden Apellidos
    VEHICULOS = "15"  # Vehículos

    @classmethod
    def all_procedures(cls) -> dict[str, str]:
        """Get all procedures as a dictionary of ID: Name."""
        return {
            "6": "Renovación Chileno/a",
            "9": "Reimpresión cédula",
            "10": "Renovación Extranjero/a",
            "11": "Solicitud de Pasaporte",
            "12": "Menores de Edad",
            "13": "Apostilla",
            "14": "Rectificaciones",
            "15": "Vehículos",
        }


class Region:
    """Chilean region IDs for SRCEI."""

    TARAPACA = "1"
    ANTOFAGASTA = "2"
    ATACAMA = "3"
    COQUIMBO = "4"
    VALPARAISO = "5"
    OHIGGINS = "6"  # Libertador General Bernardo O'Higgins
    MAULE = "7"
    BIO_BIO = "8"
    ARAUCANIA = "9"
    LOS_LAGOS = "10"
    AYSEN = "11"  # Aysén del General Carlos Ibáñez del Campo
    MAGALLANES = "12"  # Magallanes y de la Antártica Chilena
    METROPOLITANA = "13"  # Región Metropolitana de Santiago
    LOS_RIOS = "14"
    ARICA_PARINACOTA = "15"
    NUBLE = "16"

    @classmethod
    def all_regions(cls) -> dict[str, str]:
        """Get all regions as a dictionary of ID: Name."""
        return {
            "1": "REGION DE TARAPACA",
            "2": "REGION DE ANTOFAGASTA",
            "3": "REGION DE ATACAMA",
            "4": "REGION DE COQUIMBO",
            "5": "REGION DE VALPARAISO",
            "6": "REGION DEL LIBERTADOR GENERAL BERNARDO O'HIGGINS",
            "7": "REGION DEL MAULE",
            "8": "REGION DEL BIO BIO",
            "9": "REGION DE LA ARAUCANIA",
            "10": "REGION DE LOS LAGOS",
            "11": "REGION DE AYSEN DEL GENERAL CARLOS IBAÑEZ DEL CAMPO",
            "12": "REGION DE MAGALLANES Y DE LA ANTARTICA CHILENA",
            "13": "REGION METROPOLITANA DE SANTIAGO",
            "14": "REGION DE LOS RIOS",
            "15": "REGION DE ARICA Y PARINACOTA",
            "16": "REGION DE ÑUBLE",
        }
