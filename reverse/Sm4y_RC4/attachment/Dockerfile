FROM batonogov/pyinstaller-windows:latest AS builder

WORKDIR /build
COPY Sm4y_RC4.py .

RUN pyinstaller \
        --onefile \
        --clean \
        --noconfirm \
        --name Sm4y_RC4 \
        --distpath /build \
        --workpath /tmp/pyinstaller \
        --specpath /tmp/pyinstaller \
        Sm4y_RC4.py

FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends wine \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /build/Sm4y_RC4.exe /app/Sm4y_RC4.exe

CMD ["wine", "/app/Sm4y_RC4.exe"]
