namespace Atrasis.Laser.Battle.Logic.Modes
{
    using Atrasis.Laser.Battle.DataStream;
    using Atrasis.Laser.Battle.Logic.Input;
    using System.Collections.Generic;

    // ─────────────────────────────────────────────────────────────────────────────
    // IBattleMode : 한 배틀 세션의 시뮬레이션 로직 인터페이스.
    //
    // 새 게임 모드를 추가하는 방법 (예: Gem Grab, Showdown, Heist ...):
    //   1. IBattleMode를 구현하는 새 클래스를 Modes/ 아래에 만든다.
    //      - BrawlBallMode.cs 를 참고하면 된다 (가장 단순한 완성 예시).
    //   2. BattleModeRegistry.cs 에 팩토리를 등록한다.
    //   3. 로비(lobby/Logic/BattleSessions.py)의 MODE_* 상수와 숫자를 맞춘다.
    //
    // 세션 루프(Session.BattleLoop)가 매 틱(50ms)마다 Update() → Encode()를
    // 호출하고, 클라이언트 입력은 HandleInput()으로 들어온다.
    // ─────────────────────────────────────────────────────────────────────────────
    public interface IBattleMode
    {
        // BattleModeRegistry 의 상수와 동일한 값이어야 한다.
        int ModeId { get; }

        // 이 모드가 실제로 플레이 가능한 상태인지 (false면 세션 생성 시 BrawlBall로 폴백)
        bool Implemented { get; }

        // 클라이언트가 보낸 조작 입력(이동/공격 등) 처리
        void HandleInput(List<ClientInput> inputs);

        // 1틱(50ms) 시뮬레이션 진행
        void Update();

        // 현재 틱의 월드 상태를 클라이언트용 비트스트림으로 인코딩
        void Encode(BitStream stream);
    }
}
