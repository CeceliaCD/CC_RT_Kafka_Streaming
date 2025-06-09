FROM python:3.10-slim

# Installing required system dependencies
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 \
    libxss1 libappindicator3-1 libasound2 libatk-bridge2.0-0 libgtk-3-0 \
    libx11-xcb1 xdg-utils fonts-liberation libxcomposite1 libxdamage1 \
    libxrandr2 libgbm1 libxshmfence1 libu2f-udev libvulkan1 libpci3 \
    libdrm2 ca-certificates chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Linking chromium to google-chrome for consistency
RUN ln -s /usr/bin/chromium /usr/bin/google-chrome

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app

# sanity check
RUN google-chrome --version && chromedriver --version

CMD ["python", "amazon_shopping_transaction_producer.py"]
