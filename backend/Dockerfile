FROM node:20-slim AS builder

WORKDIR /app

# Install Python and build tools
RUN apt-get update && \
    apt-get install -y python3 python3-pip build-essential && \
    ln -s /usr/bin/python3 /usr/bin/python

COPY package.json yarn.lock ./
COPY src ./src
COPY tsconfig.json ./

RUN yarn install --frozen-lockfile && \
    yarn build

FROM node:20-slim AS runner

WORKDIR /app

# Install Python for runtime dependencies
RUN apt-get update && \
    apt-get install -y python3 && \
    ln -s /usr/bin/python3 /usr/bin/python

COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./
COPY --from=builder /app/src/db ./src/db

RUN mkdir -p data && \
    touch data/perplexica.db && \
    yarn drizzle-kit generate:sqlite && \
    yarn drizzle-kit push:sqlite

EXPOSE 3001

CMD ["node", "dist/app.js"] 