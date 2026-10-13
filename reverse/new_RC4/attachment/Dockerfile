FROM batonogov/pyinstaller-windows:latest AS builder

WORKDIR /build
COPY new_RC4.py .

RUN pyinstaller \
        --onefile \
        --clean \
        --noconfirm \
        --name new_RC4 \
        --distpath /build \
        --workpath /tmp/pyinstaller \
        --specpath /tmp/pyinstaller \
        new_RC4.py

FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends wine \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /build/new_RC4.exe /app/new_RC4.exe

CMD ["wine", "/app/new_RC4.exe"]
