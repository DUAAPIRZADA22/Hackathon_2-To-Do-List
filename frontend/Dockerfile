# Stage 1: Dependencies
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Stage 2: Builder
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
# Disable SWC binary download to avoid network timeouts
ENV NEXT_SKIP_SWC_BINARY=1
RUN npm run build

# Stage 3: Runner
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
# Ensure Next.js listens on all interfaces for Kubernetes probes
ENV HOSTNAME=0.0.0.0
ENV PORT=3000
# Add health check port environment variable
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
# Copy standalone output (server.js and minimal dependencies)
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
# Copy static files (required for Next.js standalone)
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
# Copy public files for proper asset serving
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
USER nextjs
EXPOSE 3000

# Health check for Kubernetes probes
# Next.js standalone serves on root path
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Graceful shutdown handling
STOPSIGNAL SIGTERM

# Start the server with proper signal handling
CMD ["node", "server.js"]
