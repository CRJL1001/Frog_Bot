FROM python:3.12-slim

RUN useradd -m botuser

WORKDIR /app

COPY requirments.txt .
RUN pip install --no-cache-dir -r requirments.txt

COPY bot.py .
COPY cogs ./cogs 
COPY sounds ./sounds
COPY config.py . 

RUN chown -R botuser:botuser /app: 
RUN chown -R botuser:botuser /app/data 

USER botuser
CMD ["python3", "bot.py"]
