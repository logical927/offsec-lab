FROM debian:bookworm-20260824-slim

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        ca-certificates \
        curl \
        nginx-light \
        openssh-server \
    && rm -f /etc/ssh/ssh_host_* \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 10001 target \
    && useradd \
        --uid 10001 \
        --gid target \
        --create-home \
        --shell /usr/sbin/nologin \
        target

COPY nginx.conf /etc/nginx/nginx.conf
COPY sshd_config /etc/ssh/sshd_config
COPY --chown=target:target files/index.html /usr/share/nginx/html/index.html
COPY --chmod=755 start-target.sh /usr/local/bin/start-target

USER target
WORKDIR /home/target

EXPOSE 22 80

ENTRYPOINT ["/usr/local/bin/start-target"]
