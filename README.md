# jev-fizzbuzz

Jev（`typesafe/jev-latest`、ロリポップ！AIゲートウェイ `POST /v1/systemone`）に「N は 3 / 5 で割り切れるか」だけを判断させて FizzBuzz を解く。FizzBuzz の出力を決める割り算はコードでやらない（剰余計算は問題作りと採点だけ）。

```
AI_GATEWAY_API_KEY_FILE=<キーのファイル> python3 fizzbuzz.py batch --reps 5   # 1〜100 を200問まとめて1リクエスト
AI_GATEWAY_API_KEY_FILE=<キーのファイル> python3 fizzbuzz.py single           # 1問1リクエストを逐次200回
AI_GATEWAY_API_KEY_FILE=<キーのファイル> python3 fizzbuzz.py big              # 境界値・4/6/10/20桁
AI_GATEWAY_API_KEY_FILE=<キーのファイル> python3 ladder.py                    # 桁数を増やして FizzBuzz
python3 build_page.py                                                         # results/ から index.html を生成
```

## 結果（2026-09-18 実測、生ログは results/*.jsonl）

- 1〜100: 6回とも 100/100 正解。200問まとめて1リクエストで 851 / 859 / 933 / 1004 / 1216 / 1320 ms
- 1問ずつ逐次200回: 100/100 正解、合計 146.6 秒（1回あたり p50 628 ms / p95 1216 ms）
- 桁数を増やす（ladder.py、各桁 FizzBuzz / Fizz / Buzz / 数字 を15個ずつ、2桁は48個）:

| 桁数 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 | 15 | 20 | 25 | 30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FizzBuzz 正解 | 48/48 | 60/60 | 60/60 | 60/60 | 60/60 | 60/60 | 50/60 | 50/60 | 41/60 | 37/60 | 24/60 | 27/60 |
| ÷3 正解 | 48/48 | 60/60 | 60/60 | 60/60 | 60/60 | 60/60 | 51/60 | 51/60 | 44/60 | 38/60 | 29/60 | 27/60 |
| ÷5 正解 | 48/48 | 60/60 | 60/60 | 60/60 | 60/60 | 60/60 | 59/60 | 59/60 | 55/60 | 59/60 | 52/60 | 59/60 |

崩れるのは ÷3。間違いの多くは3の倍数でない数を「割り切れる」と答えるもの（30桁で25件、逆は8件）。

ページ: https://kentarokuribayashi.com/jev-fizzbuzz/
