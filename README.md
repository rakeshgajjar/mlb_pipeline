# MLB Data Pipeline

This is a robust, production-ready data pipeline for Major League Baseball data sourced from MLB.com APIs.

## Features
- Scalable, robust configuration via environment variables.
- Retry mechanisms using `tenacity` on transient network errors.
- Extract MLB schedule data (JSON) via MLB open stats API.
- Transforms data into flat CSV format and structured XML format.
- Delivered as a Docker container.
- Includes tests and CI checks via GitHub actions.

## Requirements
- Python 3.10+
- Docker & Docker Compose (optional but recommended)

## Configuration
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Modify variables inside `.env` as needed.

## Running Locally

### Using Python Map
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the pipeline:
   ```bash
   python -m src.main
   ```
   Data will be downloaded to the output directory defined in `.env` (default `./data`).

### Using Docker Compose
1. Ensure Docker is running.
2. Build and run using Docker Compose:
   ```bash
   docker-compose up --build
   ```
   Outputs are stored in the `./data` directory relative to the repository.

## Running Tests
Ensure dev dependencies are installed (`pytest`), then run:
```bash
pytest tests/
```

## Future State (Phase 2)
Further steps will involve MariaDB insertion using an ORM like SQLAlchemy and setting up Terraform to persist runs.
