#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# jaebinbrawl-v26 원클릭 실행 스크립트
#   - 로비 서버: Python (TCP 9339)
#   - 배틀 서버: C# .NET 6 (UDP 1337)
# 오라클 리눅스 VM 등 어디서든: bash run.sh 한 줄로 의존성 확인/설치 후 두 서버 동시 구동.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")"

LOBBY_PORT="${LOBBY_PORT:-9339}"
BATTLE_PORT="${BATTLE_PORT:-1337}"
export BATTLE_PORT

SUDO=""
if [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1; then
  SUDO="sudo"
fi

log() { echo "[run.sh] $*"; }

# ── 1) Python 3 + tinydb (로비) ──────────────────────────────────────────────
if ! command -v python3 >/dev/null 2>&1; then
  log "python3 없음 → 설치"
  if command -v apt-get >/dev/null 2>&1; then
    $SUDO apt-get update -y && $SUDO apt-get install -y python3 python3-pip
  elif command -v dnf >/dev/null 2>&1; then
    $SUDO dnf install -y python3 python3-pip   # 오라클 리눅스
  elif command -v yum >/dev/null 2>&1; then
    $SUDO yum install -y python3 python3-pip
  else
    log "ERROR: python3 자동 설치 실패 — 직접 설치 후 다시 실행하세요."; exit 1
  fi
fi

if ! python3 -c 'import tinydb' >/dev/null 2>&1; then
  log "tinydb 없음 → 설치"
  python3 -m pip install --quiet tinydb \
    || $SUDO python3 -m pip install --quiet tinydb \
    || python3 -m pip install --quiet --break-system-packages tinydb
fi

# ── 2) .NET SDK 6.0 (배틀) ───────────────────────────────────────────────────
if ! command -v dotnet >/dev/null 2>&1; then
  log "dotnet 없음 → 설치 시도"
  if command -v apt-get >/dev/null 2>&1 && apt-cache show dotnet-sdk-6.0 >/dev/null 2>&1; then
    $SUDO apt-get update -y && $SUDO apt-get install -y dotnet-sdk-6.0 || true
  elif command -v dnf >/dev/null 2>&1; then
    $SUDO dnf install -y dotnet-sdk-6.0 || true
  fi
  if ! command -v dotnet >/dev/null 2>&1; then
    log "패키지 설치 실패 → dotnet-install 스크립트로 설치"
    curl -sSL https://dot.net/v1/dotnet-install.sh -o /tmp/dotnet-install.sh
    bash /tmp/dotnet-install.sh --channel 6.0 --install-dir "$HOME/.dotnet"
    export PATH="$HOME/.dotnet:$PATH"
    export DOTNET_ROOT="$HOME/.dotnet"
  fi
fi
export DOTNET_CLI_TELEMETRY_OPTOUT=1

# ── 3) 배틀 서버 빌드 ────────────────────────────────────────────────────────
log "배틀 서버 빌드 (dotnet build)"
dotnet build battle/Atrasis.Laser.Battle.sln -c Release

BATTLE_DLL="battle/Atrasis.Laser.Battle/bin/Release/net6.0/Atrasis.Laser.Battle.dll"
if [ ! -f "$BATTLE_DLL" ]; then
  log "ERROR: 빌드 결과물 없음: $BATTLE_DLL"; exit 1
fi

# ── 4) 두 서버 동시 구동 ─────────────────────────────────────────────────────
log "배틀 서버 구동 (UDP $BATTLE_PORT)"
dotnet "$BATTLE_DLL" &
BATTLE_PID=$!

log "로비 서버 구동 (TCP $LOBBY_PORT)"
(cd lobby && exec python3 main.py) &
LOBBY_PID=$!

trap 'kill $BATTLE_PID $LOBBY_PID 2>/dev/null || true' EXIT INT TERM
log "구동 완료: 로비 TCP $LOBBY_PORT / 배틀 UDP $BATTLE_PORT  (Ctrl+C로 종료)"
wait
