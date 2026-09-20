FROM python:3.12-slim

RUN useradd -m botuser

WORKDIR /app

COPY requirments.txt .
RUN pip install --no-cache-dir -r requirments.txt
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg tzdata \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=Europe/Paris

COPY bot.py .
COPY config.py .
COPY database.py .
COPY cogs ./cogs
COPY sounds ./sounds
COPY reminders.json .

RUN chown -R botuser:botuser /app

USER botuser

CMD ["python3", "bot.py"]