# =============================================================================
# Multi-stage Dockerfile for the SE4206 Flask app
# Stage 1 installs build dependencies, Stage 2 produces a slim runtime image.
# This mirrors a real production pattern (smaller, fewer attack vectors).
# =============================================================================

# ---------- Stage 1: builder ----------
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .

# Install only what's needed to build wheels; --user keeps everything under /root/.local
# so we can copy a single directory into the runtime image.
RUN pip install --no-cache-dir --user --upgrade pip \
 && pip install --no-cache-dir --user -r requirements.txt


# ---------- Stage 2: runtime ----------
FROM python:3.11-slim AS runtime

# Create a non-root user (security best practice)
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /home/appuser/app

# Bring in the pre-built dependencies from the builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application source
COPY --chown=appuser:appuser app/ ./app/

ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser

EXPOSE 5000

# Native Docker health check - works with `docker ps` and orchestrators
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request,sys; \
    sys.exit(0) if urllib.request.urlopen('http://localhost:5000/health').status==200 else sys.exit(1)" \
  || exit 1

CMD ["python", "-m", "app.main"]
