# ICS Sync Server
This is a rapidly made personal project to expose ICS files as a web service to
allow syncing some events (train tickets, sport reservations, etc.) with a
calendar supporting ICS files. In my case it's used and tested with Proton.

## Dev

```bash
# Install poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Create a .env and fill it
cp .env.example .env
nano .env

# Run the dev server
python3 main.py
```

## Deployment

Build the docker image

```bash
docker build -t ghcr.io/alabate/ics-sync-server:latest .
docker push ghcr.io/alabate/ics-sync-server:latest
```