namespace Atrasis.Laser.Battle.Logic.Modes
{
    using System;
    using System.Collections.Generic;

    // ─────────────────────────────────────────────────────────────────────────────
    // BattleModeRegistry : v26 게임 모드 ID → 구현 팩토리 매핑.
    // 로비(lobby/Logic/BattleSessions.py)의 MODE_* 상수와 반드시 같은 값을 유지할 것.
    //
    // 알 수 없는 모드 ID가 와도 크래시 나지 않게 GenericBattleMode(BrawlBall 규칙)로
    // 폴백한다. 미구현 모드는 경고를 남기고 BrawlBall(테스트 기반)로 폴백 — 클라이언트가
    // 빈 비전을 받아 멈추는 일을 막는다.
    // ─────────────────────────────────────────────────────────────────────────────
    public static class BattleModeRegistry
    {
        // ── 정규 이벤트 모드 ──
        public const int GemGrab = 0;         // 젬그랩
        public const int Showdown = 2;        // 쇼다운 (솔로 10인 / 듀오 5팀 10인)
        public const int Heist = 3;           // 하이스트
        public const int Bounty = 4;          // 바운티
        public const int BrawlBall = 5;       // 브롤볼 ✅ 구현됨 (테스트 기반)

        // ── 주말 특별 이벤트 ──
        public const int RoboRumble = 6;      // 로보 럼블
        public const int BossFight = 7;       // 보스전
        public const int BigGame = 8;         // 빅 게임

        // ── 기타 / 시즌 이벤트 ──
        public const int LoneStar = 11;       // 론 스타
        public const int Takedown = 12;       // 테이크다운
        public const int PresentPlunder = 13; // 선물 훔치기

        private static readonly Dictionary<int, Func<IBattleMode>> Factories = new Dictionary<int, Func<IBattleMode>>
        {
            { BrawlBall,      () => new BrawlBallMode()      },  // ✅ 구현됨
            { GemGrab,        () => new GemGrabMode()        },  // 스켈레톤
            { Showdown,       () => new ShowdownMode()       },  // 스켈레톤
            { Heist,          () => new HeistMode()          },  // 스켈레톤
            { Bounty,         () => new BountyMode()         },  // 스켈레톤
            { RoboRumble,     () => new RoboRumbleMode()     },  // 스켈레톤
            { BossFight,      () => new BossFightMode()      },  // 스켈레톤
            { BigGame,        () => new BigGameMode()        },  // 스켈레톤
            { LoneStar,       () => new LoneStarMode()       },  // 스켈레톤
            { Takedown,       () => new TakedownMode()       },  // 스켈레톤
            { PresentPlunder, () => new PresentPlunderMode() },  // 스켈레톤
        };

        public static bool IsKnown(int modeId) => Factories.ContainsKey(modeId);

        // 구현이 끝난 모드로 세션을 만든다.
        //  - 알려졌지만 미구현인 모드 → BrawlBall 폴백 (경고 로그)
        //  - registry에 없는 알 수 없는 모드 → GenericBattleMode (BrawlBall 규칙, 크래시 없음)
        public static IBattleMode Create(int modeId)
        {
            if (Factories.TryGetValue(modeId, out var factory))
            {
                IBattleMode mode = factory();
                if (mode.Implemented)
                {
                    return mode;
                }

                Console.WriteLine($"[WARN] mode {modeId} is registered but not implemented yet; falling back to BrawlBall.");
                return new BrawlBallMode();
            }

            Console.WriteLine($"[WARN] unknown mode id {modeId}; using GenericBattleMode (BrawlBall rules).");
            return new GenericBattleMode();
        }
    }
}
