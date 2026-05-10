FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    rsync \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install .

COPY . .

# Ensure .ssh directory exists for rsync
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh

EXPOSE 8000

CMD ["python", "server.py"]
