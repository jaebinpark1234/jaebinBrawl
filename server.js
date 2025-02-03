// server.js (Node.js + Express + Webhook 기반 자동 입금 확인 서버)

const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const PORT = 3000;

app.use(bodyParser.json());

// 사용자 포인트 데이터 저장 (실제 환경에서는 DB 사용 권장)
let userBalances = {};

// 입금 내역을 받는 Webhook 엔드포인트
app.post('/webhook', (req, res) => {
    const { senderName, amount, accountNumber } = req.body;

    console.log(`입금 확인: ${senderName}, 금액: ${amount}원`);

    // 특정 계좌로 입금되었을 때 포인트 추가
    if (accountNumber === "123-456-789") {  // 본인 계좌번호 설정 필요
        if (!userBalances[senderName]) userBalances[senderName] = 0;
        userBalances[senderName] += amount;

        console.log(`${senderName}님에게 ${amount} 포인트 지급 완료!`);
    }

    res.status(200).send("OK");
});

// 사용자 포인트 조회 API
app.get('/get-balance', (req, res) => {
    const user = req.query.user;
    const balance = userBalances[user] || 0;
    res.json({ balance });
});

app.listen(PORT, () => {
    console.log(`서버 실행 중... 포트: ${PORT}`);
});
