# horas-registro-civil

FastAPI backend for Chile's SRCEI civil registry appointment slots with real-time Playwright scraping.

## Overview

This API provides real-time access to available appointment slots from Chile's SRCEI (Servicio de Registro Civil e Identificación) system. It uses Playwright for browser automation to bypass WAF protection and scrapes slot data on-demand, returning results sorted chronologically (earliest first).

**Key Features:**
- Real-time slot availability
- Supports all 8 SRCEI procedures
- Supports all 16 Chilean regions
- Slots sorted by datetime (earliest first)
- Google Cloud Run deployment ready
- No authentication required (public API)

**Trade-offs:**
- Response times: 10-30 seconds (real-time browser scraping)
- No caching (always fresh data)

## API Endpoints

### GET /

Health check endpoint.

**Response:**
```json
{
  "message": "horas-registro-civil API",
  "status": "healthy",
  "version": "0.1.0"
}
```

### GET /slots

Get available appointment slots for a procedure and region.

**Query Parameters:**
- `procedure_id` (required): Procedure type ID (6-15)
  - 6 = Renovación Chileno/a
  - 9 = Reimpresión cédula
  - 10 = Renovación Extranjero/a
  - 11 = Solicitud de Pasaporte
  - 12 = Menores de Edad
  - 13 = Apostilla
  - 14 = Rectificaciones
  - 15 = Vehículos
- `region_id` (required): Chilean region ID (1-16)
  - 1 = Tarapacá
  - 2 = Antofagasta
  - 3 = Atacama
  - 4 = Coquimbo
  - 5 = Valparaíso
  - 6 = O'Higgins
  - 7 = Maule
  - 8 = Bío Bío
  - 9 = Araucanía
  - 10 = Los Lagos
  - 11 = Aysén
  - 12 = Magallanes
  - 13 = Metropolitana (Santiago)
  - 14 = Los Ríos
  - 15 = Arica y Parinacota
  - 16 = Ñuble

**Example Request:**
```bash
curl "http://localhost:8000/slots?procedure_id=6&region_id=13"
```

**Example Response:**
```json
{
  "slots": [
    {
      "office_name": "SANTIAGO CENTRO",
      "office_address": "TEATINOS 120",
      "date": "29/01/2026",
      "time": "09:30",
      "datetime_iso": "2026-01-29T09:30:00",
      "office_id": ""
    },
    {
      "office_name": "ALHUÉ",
      "office_address": "ESMERALDA S/N",
      "date": "29/01/2026",
      "time": "10:00",
      "datetime_iso": "2026-01-29T10:00:00",
      "office_id": ""
    }
  ],
  "count": 2,
  "procedure_id": "6",
  "region_id": "13",
  "scraped_at": "2026-01-09T12:34:56.789Z"
}
```

**Response Times:**
- Typical: 10-30 seconds (real-time browser scraping)
- First request after cold start: 30-60 seconds (includes browser initialization)

**Error Codes:**
- 400: Invalid query parameters
- 503: Failed to authenticate with SRCEI or service unavailable
- 504: Gateway timeout (scraping took too long)
- 500: Internal server error

## Development

### Prerequisites

- Python 3.12+
- uv (Python package manager)
- Docker (optional, for containerized deployment)

### Local Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd horas-registro-civil
```

2. Create virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
make install-dev
```

3. Install Playwright browsers:
```bash
make install-browsers
```

4. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your SRCEI credentials
```

5. Run development server:
```bash
make local-server
```

API will be available at `http://localhost:8000`

### Environment Variables

Required:
- `SRCEI_RUT`: Chilean RUT with dash (e.g., "12345678-9")
- `SRCEI_PASSWORD`: SRCEI account password

Optional:
- `PORT`: Server port (default: 8080)
- `ENVIRONMENT`: Environment name (default: "production")

### Running Tests

```bash
make test
```

### Code Quality

```bash
# Lint
make lint

# Format
make fmt
```

## Docker

### Build Image

```bash
make build-to-deploy
```

### Run Container Locally

```bash
make run-docker
```

## Deployment

### Google Cloud Run

#### Prerequisites

1. GCP project with Cloud Run and Artifact Registry enabled
2. Service account with necessary permissions
3. Secrets configured in GCP Secret Manager:
   - `SRCEI_RUT`
   - `SRCEI_PASSWORD`

#### GitHub Actions Deployment

1. Configure GitHub secrets:
   - `GCP_PROJECT_ID`: Your GCP project ID
   - `SA_KEY`: Service account JSON key

2. Push to main branch:
```bash
git push origin main
```

GitHub Actions will automatically:
- Build Docker image
- Push to Google Artifact Registry
- Deploy to Cloud Run

#### Manual Deployment

```bash
# Build and push image
docker build --platform linux/amd64 -t horas-registro-civil:latest .
docker tag horas-registro-civil:latest us-docker.pkg.dev/PROJECT_ID/REPO/api:latest
docker push us-docker.pkg.dev/PROJECT_ID/REPO/api:latest

# Deploy to Cloud Run
gcloud run deploy horas-registro-civil \
  --image us-docker.pkg.dev/PROJECT_ID/REPO/api:latest \
  --region us-west2 \
  --memory 1024Mi \
  --timeout 300 \
  --max-instances 10 \
  --allow-unauthenticated \
  --set-secrets SRCEI_RUT=SRCEI_RUT:latest,SRCEI_PASSWORD=SRCEI_PASSWORD:latest
```

## Architecture

### Tech Stack

- **Framework**: FastAPI (async Python web framework)
- **Browser Automation**: Playwright (async API)
- **Language**: Python 3.12
- **Deployment**: Google Cloud Run (serverless containers)
- **Package Manager**: uv (fast Python package manager)

### Key Components

- `src/api/main.py`: FastAPI application setup
- `src/api/routers/slots.py`: Slots endpoint implementation
- `src/services/srcei/client.py`: Playwright client for scraping
- `src/services/srcei/recommender.py`: Slot sorting utilities
- `src/services/srcei/config.py`: SRCEI configuration and constants
- `src/schemas/slots.py`: Pydantic models for API

### Real-Time Scraping Flow

1. API request received
2. Create new Playwright browser instance
3. Navigate to SRCEI website
4. Login with credentials
5. Select procedure and region
6. Scrape slots from DOM using JavaScript
7. Parse and sort slots chronologically
8. Close browser
9. Return JSON response

**Browser Lifecycle**: Each request creates a new browser instance which is closed after scraping. No browser pooling in v1 for simplicity.

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Future Enhancements

- Browser pooling for faster responses
- Short-term caching (30s) for duplicate queries
- GET /slots/office/{office_id} endpoint
- Rate limiting
- Metrics and monitoring dashboard
- Historical slot availability tracking

## Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

[Add your license here]

## Support

For issues or questions:
- GitHub Issues: [repository-url]/issues
- Documentation: This README

## Related Projects

- [ainda/maind-backend](../maind-backend): Reference FastAPI backend
- [ainda/prototypes/srcei_appointment_finder](../prototypes/srcei_appointment_finder): Original prototype implementation
