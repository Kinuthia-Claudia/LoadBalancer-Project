FROM python:3.9-slim

WORKDIR /app

COPY load_balancer.py .
COPY hashing.py .

RUN apt-get update && \
    apt-get install -y curl gnupg apt-transport-https ca-certificates lsb-release && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y docker-ce-cli

RUN pip install flask

EXPOSE 5000

CMD ["python", "load_balancer.py"]
