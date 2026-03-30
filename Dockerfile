FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8501

WORKDIR /app

COPY App/requirements.txt /app/App/requirements.txt

RUN python -m pip install --upgrade pip && \
    python -m pip install -r /app/App/requirements.txt

COPY . /app

RUN chmod +x /app/start.sh && mkdir -p /app/App/Uploaded_Resumes

EXPOSE 8501

CMD ["bash", "/app/start.sh"]
