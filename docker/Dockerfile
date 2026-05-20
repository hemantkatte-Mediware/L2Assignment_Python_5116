# =============================================================================
# Dockerfile — OrangeHRM Automation
# =============================================================================
# Multi-stage build:
#   Stage 1 (base): Python + Chrome + ChromeDriver
#   Stage 2 (app):  Install Python deps and copy source code
# =============================================================================

FROM python:3.11-slim AS base

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Chrome and its dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
    xvfb \
    libgconf-2-4 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome stable
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
       > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# ── App stage ─────────────────────────────────────────────────────────────────
FROM base AS app

WORKDIR /app

# Copy and install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project
COPY . .

# Create output directories
RUN mkdir -p reports screenshots allure-results

# Force headless mode inside the container (no display available)
ENV HEADLESS=true
ENV BROWSER=chrome

# Default command: run the full test suite with HTML + Allure reports
CMD ["sh", "-c", \
     "behave \
       --format allure_behave.formatter:AllureFormatter \
       --outfile allure-results \
       --format behave_html_formatter:HTMLFormatter \
       --outfile reports/report.html \
       --format progress2 \
       --no-capture \
     || true"]
