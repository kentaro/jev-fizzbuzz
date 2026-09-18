"""桁数を増やしながら FizzBuzz を解かせ、Jev が何桁まで正しく答えられるかを測る。

各桁数で FizzBuzz / Fizz / Buzz / 数字 の4種類を15個ずつ（2桁は FizzBuzz が6個しかないので6個）選び、
「3で割り切れるか」「5で割り切れるか」をまとめて1リクエストで投げる。剰余計算は問題作りと採点だけに使う。

  AI_GATEWAY_API_KEY_FILE=<キーのファイル> python3 ladder.py
"""
import json
import pathlib
import random

import jev
from fizzbuzz import STATE, fizzbuzz_from, questions_for, truth

DIGITS = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30]
PER_KIND = 15
OUT = pathlib.Path(__file__).parent / "results" / "ladder.jsonl"


def pick(rng, digits):
    lo, hi = 10 ** (digits - 1), 10 ** digits - 1
    kinds = {"FizzBuzz": set(), "Fizz": set(), "Buzz": set(), "number": set()}
    if digits <= 2:
        for n in range(lo, hi + 1):
            kinds[truth(n) if not truth(n).isdigit() else "number"].add(n)
        return sorted(n for s in kinds.values() for n in rng.sample(sorted(s), min(PER_KIND, len(s))))
    while any(len(s) < PER_KIND for s in kinds.values()):
        n = rng.randint(lo, hi)
        k = truth(n) if not truth(n).isdigit() else "number"
        if len(kinds[k]) < PER_KIND:
            kinds[k].add(n)
    return sorted(n for s in kinds.values() for n in s)


def main():
    rng = random.Random(125841)
    OUT.parent.mkdir(exist_ok=True)
    for digits in DIGITS:
        nums = pick(rng, digits)
        status, ms, data = jev.call(STATE, questions_for(nums), timeout=120)
        rec = {"digits": digits, "status": status, "ms": round(ms), "questions": len(nums) * 2,
               "usage": data.get("usage"), "error": data.get("error"), "items": []}
        if status == 200:
            a = data["answers"]
            for n in nums:
                p3, p5 = a[f"n{n}_3"]["noul"], a[f"n{n}_5"]["noul"]
                got = fizzbuzz_from(p3, p5, n)
                rec["items"].append({"n": str(n), "p3": p3, "p5": p5, "got": got, "want": truth(n), "ok": got == truth(n),
                                     "ok3": (p3 >= 0.5) == (n % 3 == 0), "ok5": (p5 >= 0.5) == (n % 5 == 0)})
        with open(OUT, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        it = rec["items"]
        print(json.dumps({"digits": digits, "status": status, "ms": rec["ms"], "n": len(it),
                          "fizzbuzz": sum(i["ok"] for i in it), "div3": sum(i["ok3"] for i in it),
                          "div5": sum(i["ok5"] for i in it)}))


if __name__ == "__main__":
    main()
