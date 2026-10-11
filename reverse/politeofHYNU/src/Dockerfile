FROM ubuntu:22.04 AS build
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc make libc6-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY . /src/
RUN make && gcc -O2 -Wall -o /wrap wrap.c

FROM debian:bookworm-slim
COPY --from=build /src/client.elf /app/client.elf
COPY --from=build /src/server.elf /app/server.elf
COPY --from=build /wrap /app/wrap
WORKDIR /app
EXPOSE 9999
# FLAG 只在运行时注入（环境变量或 /flag），不要写进镜像。
CMD ["/app/wrap"]
