FROM ghcr.io/home-assistant/base:latest

RUN apk add --no-cache python3 py3-pip
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY citabot.py /app/
CMD ["python", "/app/citabot.py"]
