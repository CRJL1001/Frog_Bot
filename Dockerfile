FROM python:3.12-slim

RUN useradd -m botuser

WORKDIR /app

COPY requirments.txt .
RUN pip install --no-cache-dir -r requirments.txt
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY bot.py .
COPY config.py .
COPY database.py .
COPY cogs ./cogs
COPY sounds ./sounds
COPY data/reminders.json .

RUN chown -R botuser:botuser /app

USER botuser

CMD ["python3", "bot.py"]