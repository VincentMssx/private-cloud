FROM python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
WORKDIR /srv
COPY requirements.txt .
RUN --mount=type=secret,id=ca_bundle if [ -f /run/secrets/ca_bundle ]; then export PIP_CERT=/run/secrets/ca_bundle; fi; pip install --no-cache-dir -r requirements.txt
COPY --chmod=0444 *.py ./
USER 65534:65534
CMD ["python","server.py"]
