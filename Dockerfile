FROM python:3.10-slim-bullseye

RUN apt update
RUN apt install -y curl
HEALTHCHECK --interval=10s --timeout=3s CMD curl -s -f http://localhost:8888 || exit 1

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY asyncio_graceful_shutdown.py main.py

ENTRYPOINT ["python3", "main.py"]