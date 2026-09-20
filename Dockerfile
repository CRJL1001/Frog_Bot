FROM python:3.12-slim

RUN useradd -m botuser

WORKDIR /app

COPY requirments.txt .
RUN pip install --no-cache-dir -r requirments.txt

COPY bot.py .
COPY cogs . 
COPY sounds . 
COPY config.py . 

USER botuser

CMD ["python3", "bot.py"]
