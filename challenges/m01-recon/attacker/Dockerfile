FROM debian:bookworm-20260824-slim

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        bash \
        ca-certificates \
        curl \
        dnsutils \
        iproute2 \
        iputils-ping \
        nmap \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1000 trainee \
    && useradd \
        --uid 1000 \
        --gid trainee \
        --create-home \
        --shell /bin/bash \
        trainee

USER trainee
WORKDIR /home/trainee

CMD ["sleep", "infinity"]
