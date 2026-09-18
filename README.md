# jev-fizzbuzz

Jev（`typesafe/jev-latest`、ロリポップ！AIゲートウェイ `POST /v1/systemone`）に「N は 3 / 5 で割り切れるか」だけを判断させて FizzBuzz を解く。FizzBuzz の出力を決める割り算はコードでやらない（剰余計算は問題作りと採点だけ）。

```
AI_GATEWAY_API_KEY_FILE=<キーのファイル> python3 fizzbuzz.py batch --reps 5   # 1〜100 を200問まとめて1リクエスト
AI_GATEWAY_API_KEY_FILE=<キーのファイル> python3 fizzbuzz.py single           # 1問1リクエストを逐次200回
AI_GATEWAY_API_KEY_FILE=<キーのファイル> python3 fizzbuzz.py big              # 境界値・4/6/10/20桁
AI_GATEWAY_API_KEY_FILE=<キーのファイル> python3 ladder.py                    # 桁数 × 割る数 の正答率マップ
python3 build_page.py                                                         # results/ から page.html を生成
```

## 結果（2026-09-18 実測、生ログは results/*.jsonl）

- 1〜100: 6回とも 100/100 正解。200問まとめて1リクエストで 851 / 859 / 933 / 1004 / 1216 / 1320 ms
- 1問ずつ逐次200回: 100/100 正解、合計 146.6 秒（1回あたり p50 628 ms / p95 1216 ms）
- 大きい数の FizzBuzz 正答率（各100数を1リクエスト）: 4桁 100% / 6桁 99% / 10桁 92% / 20桁 52%。20桁でも ÷5 は 99%、崩れているのは ÷3（53%）
- 桁数 × 割る数（ladder.py、各マス20問・半数は割り切れる数）: ÷2・÷4・÷5・÷10 は30桁まで 17〜20/20。÷3 は20桁以降 9〜12/20、÷9 は15桁以降 6〜10/20（偶然なら10/20）。÷11 は5桁で 12/20、6桁以降は約10/20（6桁では「割り切れる」と一度も答えず、全部「いいえ」）
