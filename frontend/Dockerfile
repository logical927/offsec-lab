FROM node:24-alpine AS build

ENV PNPM_HOME=/pnpm
ENV PATH=$PNPM_HOME:$PATH

WORKDIR /app

RUN corepack enable

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .

ARG API_BASE_URL=http://backend:8000
ENV API_BASE_URL=$API_BASE_URL

RUN pnpm build

FROM node:24-alpine AS runtime

ENV NODE_ENV=production
ENV API_BASE_URL=http://backend:8000

WORKDIR /app

RUN addgroup -S app \
    && adduser -S -G app app

COPY --from=build --chown=app:app /app/package.json /app/pnpm-lock.yaml /app/pnpm-workspace.yaml ./
COPY --from=build --chown=app:app /app/node_modules ./node_modules
COPY --from=build --chown=app:app /app/.next ./.next

USER app

EXPOSE 3000

CMD ["node", "node_modules/next/dist/bin/next", "start", "--hostname", "0.0.0.0", "--port", "3000"]
