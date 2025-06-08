FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y \
    gcc \
    poppler-utils \
    libgl1 \
    build-essential \
    && apt-get clean
ENV PYTHONPATH=/app

WORKDIR /app
COPY ./app .
RUN pip install --upgrade pip && \
    pip install poetry

RUN poetry config virtualenvs.create false \
    && poetry install --no-root

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]