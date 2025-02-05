FROM node:20-slim AS builder

WORKDIR /app

# Install Python and build tools
RUN apt-get update && \
    apt-get install -y python3 python3-pip build-essential && \
    ln -s /usr/bin/python3 /usr/bin/python

COPY ui/package.json ui/yarn.lock ./
RUN yarn install --frozen-lockfile

COPY ui/app ./app
COPY ui/components ./components
COPY ui/lib ./lib
COPY ui/public ./public
COPY ui/next.config.js ./
COPY ui/postcss.config.js ./
COPY ui/tailwind.config.ts ./
COPY ui/tsconfig.json ./

ENV NODE_ENV=production
RUN yarn build

FROM node:20-slim AS runner

WORKDIR /app

ENV NODE_ENV=production

# Install Python for runtime dependencies
RUN apt-get update && \
    apt-get install -y python3 && \
    ln -s /usr/bin/python3 /usr/bin/python

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next/standalone ./

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"] 