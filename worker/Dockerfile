FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN --mount=type=secret,id=ca_bundle if [ -f /run/secrets/ca_bundle ]; then export PIP_CERT=/run/secrets/ca_bundle; fi; pip install --no-cache-dir -r requirements.txt
COPY --chmod=0444 *.py ./
USER 65534:65534
CMD ["python","server.py"]
