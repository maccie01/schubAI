# Build stage
FROM node:20-bullseye AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    build-essential \
    sqlite3 \
    libsqlite3-dev && \
    rm -rf /var/lib/apt/lists/*

# Set up environment
ENV npm_config_build_from_source=true

COPY package.json yarn.lock ./

# Install dependencies including better-sqlite3
RUN yarn config set python /usr/bin/python3 && \
    yarn add better-sqlite3 && \
    yarn install --network-timeout 600000

COPY src ./src
COPY tsconfig.json drizzle.config.ts ./

# Build the application and prepare migrations
RUN yarn build && \
    mkdir -p drizzle && \
    yarn drizzle-kit generate:sqlite && \
    mkdir -p data && \
    touch data/perplexica.db && \
    yarn drizzle-kit push:sqlite

# Production stage
FROM node:20-bullseye-slim AS runner

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    sqlite3 \
    libsqlite3-0 && \
    rm -rf /var/lib/apt/lists/*

# Copy build artifacts and dependencies
COPY --from=builder /build/dist ./dist
COPY --from=builder /build/node_modules ./node_modules
COPY --from=builder /build/package.json ./
COPY --from=builder /build/tsconfig.json ./
COPY --from=builder /build/drizzle.config.ts ./
COPY --from=builder /build/drizzle ./drizzle
COPY --from=builder /build/src/db/schema.ts ./src/db/schema.ts

# Create necessary directories and set permissions
RUN mkdir -p data uploads config src/db && \
    chown -R node:node /app && \
    chmod -R 755 /app

# Set resource constraints for container
ENV NODE_OPTIONS="--max-old-space-size=8192 --max-semi-space-size=512"
ENV UV_THREADPOOL_SIZE=8

# Switch to non-root user
USER node

# Health check with resource monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "const os=require('os');const used=process.memoryUsage();if(used.heapUsed>7.5e9||os.loadavg()[0]>0.9)process.exit(1);require('http').request({host:'localhost',port:3001,path:'/health',timeout:2000},(res)=>process.exit(res.statusCode===200?0:1)).end()"

# Resource limits
LABEL com.docker.container.memory="8g"
LABEL com.docker.container.cpu="4"

# Run database migrations and start the application
CMD yarn db:push && node dist/app.js