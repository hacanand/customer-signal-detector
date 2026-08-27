# Use the official Python slim image as the base
FROM python:3.12-slim

# Install Node.js (required for Next.js) and curl
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# ==========================================
# 1. Setup Backend (FastAPI)
# ==========================================
# Copy backend requirements and install them
COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the rest of the backend source code
COPY backend/ backend/

# ==========================================
# 2. Setup Frontend (Next.js)
# ==========================================
# Copy frontend dependency files
# Note: Next.js works perfectly with npm install even if you used pnpm locally
COPY frontend/package.json frontend/
# Copy the rest of the frontend source code
COPY frontend/ frontend/

# Install dependencies and build Next.js for production
RUN cd frontend && npm install && npm run build

# ==========================================
# 3. Final Configuration
# ==========================================
# Copy the start script
COPY start.sh /app/
RUN chmod +x /app/start.sh

# Expose Koyeb's default port (3000)
ENV PORT=3000
EXPOSE $PORT

# Start both services
CMD ["/app/start.sh"]
