# syntax=docker/dockerfile:1
FROM oven/bun:1-debian-slim AS base

LABEL org.opencontainers.image.title="AgenticWorkflow"
LABEL org.opencontainers.image.description="Pluripotent stem-cell framework and universal agentic toolchain for autonomous workflows"
LABEL org.opencontainers.image.url="https://github.com/imMamdouhaboammar/agentic-workflow"
LABEL org.opencontainers.image.source="https://github.com/imMamdouhaboammar/agentic-workflow"
LABEL org.opencontainers.image.licenses="MIT"

# Install Python 3, Git, and essential runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-yaml \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency manifests
COPY package.json bun.lock* pyproject.toml ./

# Install Bun dependencies
RUN bun install --frozen-lockfile || bun install

# Copy application code
COPY . .

# Link CLI executable
RUN chmod +x bin/cli.js install.sh && \
    ln -sf /app/bin/cli.js /usr/local/bin/agentic-workflow

# Default workdir volume for workflow execution
VOLUME ["/workspace"]
WORKDIR /workspace

ENTRYPOINT ["agentic-workflow"]
CMD ["--help"]
