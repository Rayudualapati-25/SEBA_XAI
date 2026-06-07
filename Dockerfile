# Reproducibility container for SEBA-XAI.
#
# Build:   docker build -t seba-xai:0.1.0 .
# Run all: docker run --rm -v "$PWD/results:/app/results" seba-xai:0.1.0 make reproduce
# Tests:   docker run --rm seba-xai:0.1.0 make test
#
# The image is intentionally minimal: stdlib + numpy/pandas/scikit-learn.
# No PyTorch, no Fabric, no GPU dependency.

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends make ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first so the layer caches between code-only changes.
COPY pyproject.toml README.md ./
COPY src ./src
COPY tests ./tests
COPY scripts ./scripts
COPY prototype ./prototype
COPY Makefile ./

RUN pip install -e ".[dev]"

# Smoke test inside the image so docker build fails loudly if the
# environment is broken.
RUN make test

CMD ["make", "help"]
