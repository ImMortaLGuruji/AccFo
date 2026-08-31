FROM python:3.11-alpine

WORKDIR /app

COPY sync_server/server.py /app/server.py

EXPOSE 8765

ENV ACCFO_SYNC_TOKEN="accfo_secret_token"

CMD ["python", "server.py", "8765"]
