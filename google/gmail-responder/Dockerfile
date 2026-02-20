FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV GOOGLE_SERVICE_ACCOUNT_JSON=""
ENV GMAIL_USER_EMAIL="me"

CMD ["python", "-m", "src.responder"]
