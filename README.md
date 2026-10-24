# 🚀 jaebinbrawl-v26 — 통합 서버 (로비 Python + 배틀 C#)

브롤스타즈 v26 사설 서버를 하나의 저장소에서 즉시 띄울 수 있게 통합한 프로젝트.

| 구성 요소 | 언어 | 포트 | 역할 |
|---|---|---|---|
| `lobby/` 로비 서버 | Python 3 (tinydb) | **TCP 9339** | 로그인, 홈, 상점, **클럽**, **순위표**, **전투 기록**, **팀방(친선전)** |
| `battle/` 배틀 서버 | C# .NET 6 | **UDP 1337** | 실시간 배틀 시뮬레이션 (20 tick/s) |

```
클라이언트 ──TCP 9339──▶ 로비 서버(Python)
                            │  배틀 시작 시:
                            │  ① 배틀 서버로 UDP "세션 등록" (sid, 모드, 배틀 ID)
                            │  ② 클라이언트 전원에게 24109(TeamGameStartingData):
                            │     배틀 서버 IP / UDP 포트 / sid 브로드캐스팅
클라이언트 ──UDP 1337──▶ 배틀 서버(C#)  ◀── sid로 세션 식별, 입력→시뮬레이션→비전 송신
```

---

## ⚡ 원클릭 실행

### 방법 1 — run.sh (오라클 리눅스/우분투 등 리눅스 VM)

```bash
git clone https://github.com/jaebinpark1234/jaebinbrawl-v26.git
cd jaebinbrawl-v26
bash run.sh
```

`run.sh`가 알아서 처리합니다:
1. Python 3 / tinydb 설치 확인 (없으면 설치)
2. .NET SDK 6.0 설치 확인 (apt/dnf → dotnet-install 스크립트 폴백)
3. 배틀 서버 `dotnet build`
4. 로비(TCP 9339) + 배틀(UDP 1337) 동시 구동

### 방법 2 — Docker

```bash
git clone https://github.com/jaebinpark1234/jaebinbrawl-v26.git
cd jaebinbrawl-v26
docker compose up -d --build
```

두 서버가 한 컨테이너에서 함께 뜹니다.

---

## 🌐 오라클 클라우드 방화벽 개방 (TCP 9339 / UDP 1337)

VM 외부 접속을 하려면 **두 군데**를 열어야 합니다.

### 1) OCI 콘솔 — Security List (또는 NSG)
VCN → 서브넷 → Security List에 Ingress Rule 추가:

| Source CIDR | IP Protocol | Destination Port |
|---|---|---|
| 0.0.0.0/0 | TCP | 9339 |
| 0.0.0.0/0 | UDP | 1337 |

### 2) VM OS 내부 — iptables (오라클 리눅스 기본 이미지는 OS 방화벽이 막혀 있음)

```bash
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 9339 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p udp --dport 1337 -j ACCEPT
sudo netfilter-persistent save   # 또는: sudo service iptables save
```

> 오라클 리눅스(OL7/OL8)는 `/etc/sysconfig/iptables`에 기본 REJECT 규칙이 있어서
> OCI Security List만 열면 안 되고 OS iptables도 열어야 접속됩니다.

### 3) 확인

```bash
sudo ss -ltnp | grep 9339    # 로비 (TCP LISTEN)
sudo ss -lunp | grep 1337    # 배틀 (UDP)
```

---

## 📱 클라이언트 연결

v26 클라이언트(예: v26.165/v26.184)의 frida-gadget 설정에서 서버 IP를 바꿉니다:
`/lib/armeabi-v7a/libgg.config.so` 안의 `redirectHost` 값을 VM 공인 IP로.

```json
{"interaction":{"interaction":{"type":"script","path":"libscript.so","on_change":"reload","parameters":{"redirectHost":"서버_공인_IP","relocate":true}}}}
```

---

## 🎮 구현된 기능

### 로비 서버 (Python)
- **계정/홈**: 로그인, 닉네임, 프로필, 튜토리얼
- **클럽**: 생성(14301) / 가입(14305) / 탈퇴(14308) / 채팅(14315) / 설정 변경(14316) / 클럽 검색(14324) / 클럽 메일(14330) / 멤버 관리(14306)
- **순위표(14403)**: 글로벌/로컬 × (플레이어 트로피 / 클럽) 랭킹 — DB 전체 조회 후 정렬
- **전투 기록**: 배틀 종료(14110) 시 `Database/BattleLog/<플레이어ID>.json`에 전적 자동 저장 → 프로필 조회(14113) 시 BattleLogMessage(23458)로 최대 50판 전송
- **팀방(친선전)**: 방 생성(14350) / 퇴장(14353) / 멤버 상태·준비(14361) / 맵 선택(14363) / 브롤러·스킨 변경(14354) / 방해금지(14777)
- **매치메이킹**: 15초 봇 자동 충원 (아래 전용 섹션)
- **상점/상자**: 오퍼 구매, 상자 구매·오픈(브롤러 해금, PP, 골드, 젬, 티켓 랜덤 보상)

### 팀플레이 → 배틀 진입 흐름 (핵심 연동)
1. 팀방에서 **방장이 시작**(OnPlay, 14103)을 누른다.
2. 로비가 `battle_id`(난수)를 배정하고, 멤버 전원에게 **sid = battle_id × 100 + 슬롯**을 배정한다.
3. 로비 → 배틀 서버(UDP 1337)로 **세션 등록 패킷**을 멤버 수만큼 보낸다:
   `[Int 0][Int sid][Short 0xFFFF][VInt 모드ID][VInt 배틀ID][VInt 인원]`
   → C# `Program.RegisterSession()`이 모드에 맞는 시뮬레이션으로 세션을 미리 생성.
4. 로비 → **팀원 전원의 클라이언트**에게 24109(TeamGameStartingData)를 브로드캐스팅:
   배틀 서버 IP + UDP 포트 + 각자의 sid → 전원이 같은 배틀 그룹(battle_id)으로 진입.
5. 클라이언트는 UDP 1337로 sid를 붙여 입력을 보내고, 배틀 서버가 20 tick/s로 비전(월드 상태)을 되돌려준다.

### 배틀 서버 (C#) — 모드별 확장 구조
```
battle/Atrasis.Laser.Battle/
├── Program.cs            # UDP 수신 루프 + 로비 세션 등록 핸드셰이크 (24109 비전 회신)
├── Session.cs            # sid별 세션: 입력 수신 → 모드.Update()/Encode() → 비전 송신
└── Modes/
    ├── IBattleMode.cs        # 모드 인터페이스 (HandleInput / Update / Encode)
    ├── BattleModeRegistry.cs # 모드 ID → 구현 매핑 (미구현 모드는 BrawlBall 폴백)
    ├── BrawlBallMode.cs      # ✅ 구현됨 — 브롤볼 테스트 기반 PoC
    └── SkeletonModes.cs      # 미구현 모드 스켈레톤 + GenericBattleMode 폴백
```

### 🎮 지원 게임 모드 (v26 전체)

| 모드 | ID | 상태 | 비고 |
|---|---|---|---|
| 젬그랩 (Gem Grab) | 0 | 🔧 스켈레톤 | 3v3, 젬 10개 선취 |
| 쇼다운 (Showdown) | 2 | 🔧 스켈레톤 | **솔로 10인 / 듀오 5팀 10인** |
| 하이스트 (Heist) | 3 | 🔧 스켈레톤 | 3v3, 금고 파괴 |
| 바운티 (Bounty) | 4 | 🔧 스켈레톤 | 3v3, 별 획득전 |
| **브롤볼 (Brawl Ball)** | 5 | ✅ **구현됨** | 테스트 기반 PoC (이동·공격·공 처리) |
| 로보 럼블 (Robo Rumble) | 6 | 🔧 스켈레톤 | 주말 이벤트, 3인 협동 방어 |
| 보스전 (Boss Fight) | 7 | 🔧 스켈레톤 | 주말 이벤트, 3인 협동 PvE |
| 빅 게임 (Big Game) | 8 | 🔧 스켈레톤 | 주말 이벤트, 1 vs 3 비대칭 |
| 론 스타 (Lone Star) | 11 | 🔧 스켈레톤 | 3팀 스타 수집 |
| 테이크다운 (Takedown) | 12 | 🔧 스켈레톤 | 데스매치 점수제 |
| 선물 훔치기 (Present Plunder) | 13 | 🔧 스켈레톤 | 시즌 이벤트, 브롤볼 변형 |
| (알 수 없는 모드 ID) | — | 🛡️ 폴백 | `GenericBattleMode`(브롤볼 규칙)로 크래시 없이 처리 |

**현재 기본 구현 상태**: C# 배틀 엔진은 원본 v26-battles의 **브롤볼 1모드 PoC**이며, 이 저장소에서 모드 인터페이스로 재구조화했습니다. 브롤볼 외 모드는 위 표의 스켈레톤 + 구현 가이드 주석으로 제공됩니다.

**다른 모드로 확장하는 방법**:
1. `Modes/`의 스켈레톤 클래스를 채우거나 `IBattleMode`를 구현한 새 클래스 추가 (절차는 `SkeletonModes.cs` 안의 가이드 주석 참고)
2. `BattleModeRegistry`의 `Implemented`를 `true`로 변경
3. 로비 `Logic/BattleSessions.py`의 `MAP_INDEX_TO_MODE`에 맵 인덱스 → 모드 ID 매핑 확인

### ⏱️ 15초 매치메이킹 봇 자동 충원 시스템

동시 접속자가 적어도 게임이 멈추지 않습니다 (`lobby/Logic/Matchmaking.py`):
- 팀방 없이 배틀을 시작하면 **모드별 대기열**에 들어갑니다 (정원: 3v3 계열 6명, 쇼다운 10명, 보스전/로보럼블 3인 협동, 빅게임 4인).
- 대기 중 정원이 차면 **즉시 시작**합니다.
- **15초** 안에 정원이 안 차면 부족한 슬롯을 **AI 봇**(봇 닉네임 + 랜덤 브롤러/트로피)으로 자동 백필하고 지체 없이 배틀을 시작합니다.
- 시작 시 실제 플레이어 전원에게 배틀 서버(UDP 1337) 세션을 등록하고 24109로 접속 정보를 발송합니다.

---

## ⚖️ 진짜 브롤식 육성 밸런스 적용

사설 서버 특유의 무한 재화(999999 젬 등) 설정을 **전부 폐기**하고, 계정을 키우는 맛이 있도록 재설계했습니다. `config.json` 기본값과 신규 유저 템플릿에 박아 두었습니다.

| 항목 | 기존 (폐기) | 새 기본값 |
|---|---|---|
| 골드 | 20,000 | **200** |
| 보석 | 1,000,000 | **30** |
| 티켓 / 스타포인트 | 666 / 999 | **0 / 0** |
| 브롤/대형 상자 | 10,000 / 100 | **0 / 0** |
| 트로피 (계정/브롤러별) | — | **0부터 시작** (대전 승리 시 획득 → 순위표 반영) |
| 해금 브롤러 | 전원 또는 다수 | **쉘리(ID 0)만** — 나머지는 상자에서 획득 |
| 파워 레벨 | 8 (만렙) | **1부터 시작** |

**정석 육성 트리 복원** (`Packets/Commands/Client/LogicUpgradeBrawler.py`):
- 레벨업은 **파워포인트(PP) + 골드**를 지불해야 합니다. 무료 만렙 폐기.
- 비용 표(원작 밸런스): 1→2 (20 PP, 20 G) · 2→3 (30, 35) · 3→4 (50, 75) · 4→5 (80, 140) · 5→6 (130, 290) · 6→7 (200, 480) · 7→8 (300, 800) · 8→9 (440, 1250), 최대 파워 9.
- 재화가 부족하면 업그레이드가 거부되고 서버 로그에 사유가 남습니다.

**트로피 로드(Trophy Road) 보상 개편**:
- 기존의 이벤트 해금 마일스톤 자리를 **대형 상자 / 메가 상자 교대 지급**으로 교체했습니다.
  (진척도 0부터 시작, 마일스톤마다 Big Box → Mega Box 번갈아 지급 — `LogicBoxDataCommand`)
- 모든 이벤트는 **트로피 0부터 전부 플레이 가능**합니다 (이벤트 트로피 잠금 없음).
  주말 특별 이벤트(로보 럼블 · 보스전 · 빅 게임) 슬롯도 항상 활성화되어 있습니다.

**상자 드롭 확률 상향** (`Packets/Commands/Server/LogicBoxDataCommand.py`):
- 새 브롤러 등장 확률 **18% → 35%** (실험: 첫 100상자에서 평균 32~37% 해금).
- 꽝(PP만) 50% → 30%, 젬/토큰두블러 상향.
- 상자 보상량 상향: 브롤박스 코인 15~80, 대형박스 30~120, 메가박스 120~300 / PP도 각각 상향. 젬 풀에 20짜리 추가.

**상자/토큰 루프**: 배틀 결과(20400 계열)에서 승패별 스타 토큰 지급(20/15/10) → 토큰으로 브롤 상자 오픈 → PP/골드/새 브롤러 해금(`LogicBoxDataCommand`가 `UnlockedBrawlers`를 DB에 저장) → PP+골드로 파워 레벨업. 전체 루프가 서버 밸런스 값 위에서 돌아갑니다.

설정은 `lobby/config.json`에서 바꿀 수 있습니다 (`OnlineBattle`, `BattleServerIp`, `BattleServerPort` 등 포함).

---

## 🧰 설정 요약 (환경변수 / config.json)

| 변수 | 기본값 | 설명 |
|---|---|---|
| `LOBBY_PORT` | 9339 | 로비 TCP 포트 (`run.sh`/docker 환경변수) |
| `BATTLE_PORT` | 1337 | 배틀 UDP 포트 (`run.sh`/docker 환경변수) |
| `BATTLE_SERVER_IP` | 127.0.0.1 | 로비가 등록 패킷을 보내는 배틀 서버 IP (환경변수 우선, 없으면 config.json) |
| `OnlineBattle` | true | 배틀 시작을 온라인 세션으로 라우팅 (false = 기존 오프라인 연습만) |

> ⚠ 24109(TeamGameStartingData)의 클라이언트 측 인코딩은 빌드별로 차이가 있을 수 있습니다.
> 클라이언트가 배틀 진입 화면에서 멈춘다면 `lobby/Packets/Messages/Server/Battle/TeamGameStartingDataMessage.py`
> 의 필드 순서를 해당 클라이언트 빌드에 맞게 조정하세요 (파일 안에 가이드 주석 있음).
> 배틀 서버 자체는 sid 기반이라 이 패킷과 무관하게 동작합니다.

---

## 📦 출처 / 라이선스

- 로비 서버: [Mamikol/Classic-Brawl-V26-Remake](https://github.com/Mamikol/Classic-Brawl-V26-Remake) (GPL-3.0) 기반 + 통합/밸런스/핸드셰이크 확장
- 배틀 서버: [ShadowwDev/v26-battles](https://github.com/ShadowwDev/v26-battles) 기반 + 모드 구조 재편
- 본 저장소는 로비 코드가 GPL-3.0이므로 전체가 **GPL-3.0**으로 배포됩니다 (`LICENSE`).

## 📜 면책

Brawl Stars 및 관련 상표는 Supercell의 자산입니다. 이 프로젝트는 학습/연구 목적의 서버 에뮬레이터이며 Supercell과 무관합니다.
