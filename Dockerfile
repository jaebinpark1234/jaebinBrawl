# jaebinbrawl-v26 — 로비(Python) + 배틀(C# .NET 6) 통합 이미지
FROM mcr.microsoft.com/dotnet/sdk:6.0

RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-pip bash \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 배틀 서버 빌드 (레이어 캐시용으로 battle 먼저 복사)
COPY battle/ battle/
RUN dotnet build battle/Atrasis.Laser.Battle.sln -c Release

# 로비 서버
COPY lobby/ lobby/
RUN python3 -m pip install --no-cache-dir tinydb

ENV BATTLE_PORT=1337 \
    BATTLE_SERVER_IP=127.0.0.1 \
    DOTNET_CLI_TELEMETRY_OPTOUT=1

EXPOSE 9339 1337/udp

CMD ["bash", "-c", "dotnet battle/Atrasis.Laser.Battle/bin/Release/net6.0/Atrasis.Laser.Battle.dll & exec python3 lobby/main.py"]
