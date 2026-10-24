namespace Atrasis.Laser.Battle
{
    using Atrasis.Laser.Battle.DataStream;
    using Atrasis.Laser.Battle.Logic.Modes;
    using System;
    using System.Net;
    using System.Net.Sockets;

    class Program
    {
        // 배틀 서버 포트 (UDP). 환경변수 BATTLE_PORT로 변경 가능 (기본 1337).
        public static readonly int Port =
            int.TryParse(Environment.GetEnvironmentVariable("BATTLE_PORT"), out int p) ? p : 1337;

        // 로비가 세션을 미리 등록할 때 쓰는 마커. 클라이언트 입력 패킷의 3번째 필드(short)는
        // 항상 0에 가까운 값이므로 0xFFFF는 충돌하지 않는다.
        public const short RegistrationMarker = unchecked((short)0xFFFF);

        static Socket sock;

        private static Dictionary<long, Session> sessions = new Dictionary<long, Session>();

        static void Main(string[] args)
        {
            sock = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, ProtocolType.Udp);
            sock.Bind(new IPEndPoint(IPAddress.Any, Port));
            Console.WriteLine($"[INFO] Battle server listening on UDP {Port} (mode registry: BrawlBall implemented, GemGrab/Showdown skeletons)");

            while (true)
            {
                EndPoint remote = new IPEndPoint(IPAddress.Any, 0);
                byte[] buffer = new byte[256];
                sock.ReceiveFrom(buffer, ref remote);

                OnReceive(buffer, remote);
            }
        }

        private static void OnReceive(byte[] buf, EndPoint from)
        {
            ByteStream stream = new ByteStream(buf, 256);

            long sid = ((long)stream.ReadInt() << 32) | (uint)stream.ReadInt();
            short marker = stream.ReadShort();

            // ── 로비 핸드셰이크: 세션 등록 패킷 ─────────────────────────────
            // lobby/Logic/BattleSessions.py 가 배틀 시작 시 먼저 보내는 패킷.
            // [ sid(8바이트) ][ 0xFFFF ][ VInt modeId ][ VInt battleId ][ VInt playerCount ]
            // 이 패킷으로 세션의 게임 모드와 소속 배틀(팀방)을 미리 정해 둔다.
            // 이후 같은 sid로 클라이언트 입력이 오면 그 세션으로 들어간다.
            if (marker == RegistrationMarker)
            {
                int modeId = stream.ReadVInt();
                int battleId = stream.ReadVInt();
                int playerCount = stream.ReadVInt();

                RegisterSession(sid, modeId, battleId, playerCount, from);
                return;
            }

            // ── 클라이언트 입력 패킷 ───────────────────────────────────────
            if (!sessions.ContainsKey(sid))
            {
                // 로비 등록 없이 먼저 도착한 입력 → 기본 모드(BrawlBall)로 세션 생성
                Session sex = new Session(from, sid, BattleModeRegistry.Create(BattleModeRegistry.BrawlBall), 0);
                sessions.Add(sid, sex);
                sex.StartBattleThread();
            }
            else
            {
                sessions[sid].ReceiveInput(stream);
            }
        }

        private static void RegisterSession(long sid, int modeId, int battleId, int playerCount, EndPoint from)
        {
            if (sessions.ContainsKey(sid))
            {
                return;
            }

            Session session = new Session(from, sid, BattleModeRegistry.Create(modeId), battleId);
            sessions.Add(sid, session);
            session.StartBattleThread();

            Console.WriteLine($"[INFO] session {sid} registered (mode={modeId}, battle={battleId}, players={playerCount}, from={from})");
        }

        public static void Send(VisionUpdate vision, EndPoint p, int ssss)
        {
            vision.Encode();

            byte[] data = vision.Stream.GetByteArray();
            int length = vision.Stream.GetOffset();

            var stream = new ByteStream(10);

            {
                stream.WriteInt(0);
                stream.WriteInt(ssss);
                stream.WriteShort(0);

                stream.WriteVInt(24109);
                stream.WriteVInt(length);

                stream.WriteBytesWithoutLength(data, length);
            }

            byte[] packet = stream.GetByteArray();

            sock.SendTo(packet, 0, stream.GetOffset(), SocketFlags.None, p);
        }
    }
}
