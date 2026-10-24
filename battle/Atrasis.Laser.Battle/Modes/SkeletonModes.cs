namespace Atrasis.Laser.Battle.Logic.Modes
{
    using Atrasis.Laser.Battle.DataStream;
    using Atrasis.Laser.Battle.Logic.Input;
    using System.Collections.Generic;

    // ─────────────────────────────────────────────────────────────────────────────
    // GenericBattleMode : 레지스트리에 없는 알 수 없는 모드 ID의 폴백.
    // 브롤볼 규칙(구현된 시뮬레이션)을 그대로 쓰므로 세션이 크래시 나지 않고
    // 플레이 가능한 상태를 유지한다. 새 모드 구현 시 이 클래스를 복사해 시작하라.
    // ─────────────────────────────────────────────────────────────────────────────
    public class GenericBattleMode : BrawlBallMode
    {
        public new int ModeId => -1; // 알 수 없는 모드
        public new bool Implemented => true;
    }

    // ─────────────────────────────────────────────────────────────────────────────
    // 미구현 모드 스켈레톤 모음.
    // 각 모드의 구현 절차는 BrawlBallMode.cs / GemGrabMode.cs 안의 가이드 주석 참고:
    //   1. 상태 필드 정의 (플레이어/개체 사전)
    //   2. HandleInput — 이동/공격 처리
    //   3. Update — 모드 규칙(점수, 승패, 개체 스폰) 시뮬레이션
    //   4. Encode — 월드 상태를 비트스트림으로 인코딩 (packCharacter/packProjectile 재사용)
    //   5. Implemented를 true로 → 레지스트리가 자동으로 해당 모드를 사용한다.
    // ─────────────────────────────────────────────────────────────────────────────

    // 젬그랩: 양 팀 젬 10개 선취, 10초 카운트다운 승리.
    public class GemGrabMode : IBattleMode
    {
        public int ModeId => BattleModeRegistry.GemGrab;
        public bool Implemented => false; // 구현 완료 후 true
        public void HandleInput(List<ClientInput> inputs) { /* TODO */ }
        public void Update() { /* TODO */ }
        public void Encode(BitStream stream) { /* TODO */ }
    }

    // 쇼다운: 솔로 10인 / 듀오 5팀(10인) 생존전. 파워큐브 + 독가스 축소.
    // TODO: 탈락 순위를 세션에 기록해 로비의 쇼다운 결과 패킷(BattleResultShowdownMessage)과 연동.
    public class ShowdownMode : IBattleMode
    {
        public int ModeId => BattleModeRegistry.Showdown;
        public bool Implemented => false;
        public void HandleInput(List<ClientInput> inputs) { /* TODO */ }
        public void Update() { /* TODO */ }
        public void Encode(BitStream stream) { /* TODO */ }
    }

    // 하이스트: 상대 금고 파괴 (안전 HP 대미지전).
    public class HeistMode : IBattleMode
    {
        public int ModeId => BattleModeRegistry.Heist;
        public bool Implemented => false;
        public void HandleInput(List<ClientInput> inputs) { /* TODO */ }
        public void Update() { /* TODO */ }
        public void Encode(BitStream stream) { /* TODO */ }
    }

    // 바운티: 별 획득전 (킬 → 별, 20초 후 리스폰, 별 다수 팀 승리).
    public class BountyMode : IBattleMode
    {
        public int ModeId => BattleModeRegistry.Bounty;
        public bool Implemented => false;
        public void HandleInput(List<ClientInput> inputs) { /* TODO */ }
        public void Update() { /* TODO */ }
        public void Encode(BitStream stream) { /* TODO */ }
    }

    // 로보 럼블 (주말 이벤트): 6인 협동 — 로봇 물결 방어, 타워 방어 시간제.
    public class RoboRumbleMode : IBattleMode
    {
        public int ModeId => BattleModeRegistry.RoboRumble;
        public bool Implemented => false;
        public void HandleInput(List<ClientInput> inputs) { /* TODO */ }
        public void Update() { /* TODO */ }
        public void Encode(BitStream stream) { /* TODO */ }
    }

    // 보스전 (주말 이벤트): 협동 PvE — 보스 AI 패턴(돌진·탄막·소환) + 난이도 단계.
    public class BossFightMode : IBattleMode
    {
        public int ModeId => BattleModeRegistry.BossFight;
        public bool Implemented => false;
        public void HandleInput(List<ClientInput> inputs) { /* TODO */ }
        public void Update() { /* TODO */ }
        public void Encode(BitStream stream) { /* TODO */ }
    }

    // 빅 게임 (주말 이벤트): 1 vs 3 비대칭 — 대형 플레이어(보스급 스탯) vs 3인 팀.
    public class BigGameMode : IBattleMode
    {
        public int ModeId => BattleModeRegistry.BigGame;
        public bool Implemented => false;
        public void HandleInput(List<ClientInput> inputs) { /* TODO */ }
        public void Update() { /* TODO */ }
        public void Encode(BitStream stream) { /* TODO */ }
    }

    // 론 스타: 3팀 대전 스타 수집 — 일정 시간 후 가장 많은 별 보유 팀 승리.
    public class LoneStarMode : IBattleMode
    {
        public int ModeId => BattleModeRegistry.LoneStar;
        public bool Implemented => false;
        public void HandleInput(List<ClientInput> inputs) { /* TODO */ }
        public void Update() { /* TODO */ }
        public void Encode(BitStream stream) { /* TODO */ }
    }

    // 테이크다운: 데스매치 — 킬 점수제, 사망 시 파워큐브/점수 드랍.
    public class TakedownMode : IBattleMode
    {
        public int ModeId => BattleModeRegistry.Takedown;
        public bool Implemented => false;
        public void HandleInput(List<ClientInput> inputs) { /* TODO */ }
        public void Update() { /* TODO */ }
        public void Encode(BitStream stream) { /* TODO */ }
    }

    // 선물 훔치기 (시즌 이벤트): 상대 진영의 선물을 훔쳐 자기 진영으로 운반 — 브롤볼 변형 규칙.
    // TODO: 공(선물) 회수/반납 로직은 BrawlBallMode의 볼 처리를 재사용 가능.
    public class PresentPlunderMode : IBattleMode
    {
        public int ModeId => BattleModeRegistry.PresentPlunder;
        public bool Implemented => false;
        public void HandleInput(List<ClientInput> inputs) { /* TODO */ }
        public void Update() { /* TODO */ }
        public void Encode(BitStream stream) { /* TODO */ }
    }
}
