"""Jev の暗算の限界マップ: 桁数 × 割る数 ごとに「割り切れるか」を判断させ、正答率を測る。

割る数の選び方: 末尾だけ見れば分かる (2, 5, 10) / 末尾2桁 (4) / 桁の和 (3, 9) / 交代和 (11)。
各マスは割り切れる数と割り切れない数を半々にした 20 個（偶然の正答率が 50% になるように）。
1リクエストに1桁数ぶん（7割る数 × 20個 = 140問）をまとめて投げる。剰余計算は問題作りと採点だけに使う。

  AI_GATEWAY_API_KEY_FILE=<キーのファイル> python3 ladder.py
"""
import json
import pathlib
import random

import jev

DIVISORS = [2, 3, 4, 5, 9, 10, 11]
DIGITS = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30]
PER_CELL = 20
STATE = {"task": "整数の割り算の判定。各質問の数が指定の数で割り切れる（余りが0）かを答える"}
OUT = pathlib.Path(__file__).parent / "results" / "ladder.jsonl"


def sample(rng, digits, d, want_divisible, k):
    lo, hi = (1 if digits == 1 else 10 ** (digits - 1)), 10 ** digits - 1
    pool = [n for n in range(lo, hi + 1) if (n % d == 0) == want_divisible] if digits <= 2 else None
    out = set()
    while len(out) < k:
        if pool is not None:
            if len(out) >= len(pool):
                break
            out.add(rng.choice(pool))
            continue
        n = rng.randint(lo, hi)
        if (n % d == 0) == want_divisible:
            out.add(n)
    return sorted(out)


def main():
    rng = random.Random(125841)
    OUT.parent.mkdir(exist_ok=True)
    for digits in DIGITS:
        qs, meta = {}, {}
        for d in DIVISORS:
            nums = sample(rng, digits, d, True, PER_CELL // 2) + sample(rng, digits, d, False, PER_CELL // 2)
            for i, n in enumerate(nums):
                key = f"d{d}_{i}"
                qs[key] = {"type": "noul", "instructions": f"{n} は {d} で割り切れるか？"}
                meta[key] = (d, n)
        status, ms, data = jev.call(STATE, qs, timeout=120)
        rec = {"digits": digits, "status": status, "ms": round(ms), "questions": len(qs), "usage": data.get("usage"),
               "error": data.get("error"), "items": []}
        if status == 200:
            for key, (d, n) in meta.items():
                p = data["answers"][key]["noul"]
                rec["items"].append({"d": d, "n": str(n), "p": p, "truth": n % d == 0, "ok": (p >= 0.5) == (n % d == 0)})
        with open(OUT, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        acc = {d: sum(i["ok"] for i in rec["items"] if i["d"] == d) for d in DIVISORS}
        print(json.dumps({"digits": digits, "status": status, "ms": rec["ms"], "correct_of_20": acc}))


if __name__ == "__main__":
    main()
