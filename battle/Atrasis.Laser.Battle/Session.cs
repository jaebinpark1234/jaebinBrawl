namespace Atrasis.Laser.Battle
{
    using Atrasis.Laser.Battle.DataStream;
    using Atrasis.Laser.Battle.Logic.Modes;
    using System.Net;

    public class Session
    {
        public IBattleMode Mode;
        public int BattleId;
        public EndPoint EndPoint;
        public long SessionId;

        private bool started = false;

        public Session(EndPoint epta, long sessionId, IBattleMode mode, int battleId)
        {
            EndPoint = epta;
            SessionId = sessionId;
            Mode = mode;
            BattleId = battleId;
        }

        public void ReceiveInput(ByteStream priletel)
        {
            priletel.ReadVInt();
            int l = priletel.ReadVInt();

            ClientInputMessage message = new ClientInputMessage();
            message.Stream = priletel.ReadBytes(l);
            message.Decode();

            Mode.HandleInput(message.Inputs);
        }

        public void StartBattleThread()
        {
            if (!started)
            {
                started = true;

                new Thread(BattleLoop).Start();
            }
        }

        private void BattleLoop()
        {
            int tick = 1;
            while (true)
            {
                Mode.Update();

                var stream = new BitStream(new MemoryStream());
                Mode.Encode(stream);

                var update = new VisionUpdate();
                update.Tick = tick;
                update.stream = stream;
                update.InputCounter = Mode.InputCounter;

                Program.Send(update, EndPoint, (int)SessionId);

                tick++;

                Thread.Sleep(1000 / 20);
            }
        }
    }
}
