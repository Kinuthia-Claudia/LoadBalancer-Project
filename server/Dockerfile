FROM python:3.9-slim

WORKDIR /app

COPY server.py .

RUN apt-get update && apt-get install -y curl && pip install flask

EXPOSE 5000

CMD ["python", "server.py"]
