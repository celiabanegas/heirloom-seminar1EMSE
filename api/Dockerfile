# Heirloom API image.
# Two stages: dependencies are installed in a virtualenv in the first one and only that venv + the app code
# are copied to the final image (no pip cache, no build tools).

FROM python:3.13-slim AS build
WORKDIR /build
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim
# Commit SHA from CI (shown in /health); "dev" for local builds.
ARG VERSION=dev
ENV PATH="/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_VERSION=$VERSION \
    PORT=8000

# Run as an unprivileged user, never as root.
RUN useradd --create-home --uid 10001 app
COPY --from=build /venv /venv
WORKDIR /app
COPY app ./app
USER app

EXPOSE 8000
# Shell form so $PORT is expanded at runtime.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers
