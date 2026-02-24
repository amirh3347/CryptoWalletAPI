FROM python:3.10.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY ./core .
COPY ./dockerfiles/entrypoint.sh .
RUN chmod +x ./entrypoint.sh


EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]