# Build stage
FROM --platform=linux/arm64/v8 node:20-alpine AS builder

WORKDIR /build

# Build arguments for API configuration
ARG NEXT_PUBLIC_WS_URL=ws://127.0.0.1:3001
ARG NEXT_PUBLIC_API_URL=http://127.0.0.1:3001/api
ENV NEXT_PUBLIC_WS_URL=${NEXT_PUBLIC_WS_URL}
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Copy only necessary files
COPY ui/package.json ui/yarn.lock ./
RUN yarn install --frozen-lockfile --network-timeout 600000

COPY ui ./

RUN yarn build

# Production stage
FROM --platform=linux/arm64/v8 node:20-alpine AS runner

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /build/.next/standalone ./
COPY --from=builder /build/public ./public
COPY --from=builder /build/.next/static ./.next/static

# Set production environment
ENV NODE_ENV=production
ENV PORT=3000

# Set resource constraints
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1

# Use non-root user
USER node

CMD ["node", "server.js"]