FROM python:3.12-slim

RUN useradd -m botuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirments.txt

COPY bot.py .
COPY config.py .
COPY cogs ./cogs
COPY sounds ./sounds

RUN mkdir -p /app/data \
    && touch /app/data/reminders.json \
    && chown -R botuser:botuser /app

USER botuser

CMD ["python3", "bot.py"]