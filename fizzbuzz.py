"""Jev に「3で割り切れるか」「5で割り切れるか」を判断させて FizzBuzz を組む。

FizzBuzz の出力を決める割り算はコード側で一切しない。コード側の剰余計算は採点（正解との突き合わせ）だけに使う。

  AI_GATEWAY_API_KEY_FILE=<キーのファイル> python3 fizzbuzz.py batch --reps 5
  AI_GATEWAY_API_KEY_FILE=<キーのファイル> python3 fizzbuzz.py single
  AI_GATEWAY_API_KEY_FILE=<キーのファイル> python3 fizzbuzz.py big
"""
import argparse
import json
import pathlib
import random
import statistics
import time

import jev

STATE = {"task": "整数の割り算の判定。各質問の数が指定の数で割り切れる（余りが0）かを答える"}
OUT = pathlib.Path(__file__).parent / "results"


def question(n, d):
    return {"type": "noul", "instructions": f"{n} は {d} で割り切れるか？"}


def questions_for(nums):
    q = {}
    for n in nums:
        q[f"n{n}_3"] = question(n, 3)
        q[f"n{n}_5"] = question(n, 5)
    return q


def fizzbuzz_from(p3, p5, n):
    """Jev の確率だけで出力を決める。"""
    f, b = p3 >= 0.5, p5 >= 0.5
    return "FizzBuzz" if f and b else "Fizz" if f else "Buzz" if b else str(n)


def truth(n):  # 採点専用
    return "FizzBuzz" if n % 15 == 0 else "Fizz" if n % 3 == 0 else "Buzz" if n % 5 == 0 else str(n)


def score(nums, probs):
    rows = []
    for n in nums:
        p3, p5 = probs[f"n{n}_3"], probs[f"n{n}_5"]
        got = fizzbuzz_from(p3, p5, n)
        rows.append({"n": n, "p3": p3, "p5": p5, "got": got, "want": truth(n), "ok": got == truth(n),
                     "ok3": (p3 >= 0.5) == (n % 3 == 0), "ok5": (p5 >= 0.5) == (n % 5 == 0)})
    return rows


def summarize(label, rows, ms_list, extra=None):
    n = len(rows)
    s = {"label": label, "numbers": n,
         "fizzbuzz_acc": sum(r["ok"] for r in rows) / n,
         "div3_acc": sum(r["ok3"] for r in rows) / n,
         "div5_acc": sum(r["ok5"] for r in rows) / n,
         "wrong": [{k: r[k] for k in ("n", "p3", "p5", "got", "want")} for r in rows if not r["ok"]],
         "ms": [round(m) for m in ms_list],
         "rows": [{k: (str(r[k]) if k == "n" else r[k]) for k in ("n", "p3", "p5", "got")} for r in rows]}
    if extra:
        s.update(extra)
    return s


def run_batch(nums, label):
    status, ms, data = jev.call(STATE, questions_for(nums), timeout=120)
    if status != 200:
        return {"label": label, "status": status, "ms": [round(ms)], "error": data.get("error")}
    probs = {k: v["noul"] for k, v in data["answers"].items()}
    return summarize(label, score(nums, probs), [ms], {"status": status, "usage": data.get("usage")})


def cmd_batch(reps):
    nums = list(range(1, 101))
    for i in range(reps):
        s = run_batch(nums, f"batch 1〜100 を1リクエスト200問 #{i + 1}")
        emit(s, "batch")


def cmd_single():
    """バラ投げ: 1問1リクエストを逐次200回。"""
    nums = list(range(1, 101))
    probs, ms_list, fails = {}, [], []
    t0 = time.perf_counter()
    for n in nums:
        for d in (3, 5):
            key = f"n{n}_{d}"
            status, ms, data = jev.call(STATE, {key: question(n, d)})
            ms_list.append(ms)
            if status != 200:
                fails.append({"key": key, "status": status})
                probs[key] = float("nan")
                continue
            probs[key] = data["answers"][key]["noul"]
    wall = (time.perf_counter() - t0) * 1000
    s = summarize("single 1問1リクエストを逐次200回", score(nums, probs), ms_list,
                  {"wall_ms": round(wall), "fails": fails,
                   "p50": round(statistics.median(ms_list)),
                   "p95": round(sorted(ms_list)[int(len(ms_list) * 0.95) - 1])})
    s["ms"] = "omitted"
    emit(s, "single")


def cmd_big():
    """大きい数と境界。1リクエストに100数（200問）まとめて投げる。"""
    rng = random.Random(125841)
    boundary = [0, 3, 5, 15, 99, 100, 101, 999, 1000, 1001, 9999, 10000, 10005, 99999, 100000]
    groups = {
        "boundary": boundary,
        "4桁": rng.sample(range(1000, 10000), 100),
        "6桁": rng.sample(range(100000, 1000000), 100),
        "10桁": [rng.randrange(10**9, 10**10) for _ in range(100)],
        "20桁": [rng.randrange(10**19, 10**20) for _ in range(100)],
    }
    for name, nums in groups.items():
        emit(run_batch(nums, f"big {name}"), "big")


def emit(s, kind):
    OUT.mkdir(exist_ok=True)
    with open(OUT / f"{kind}.jsonl", "a") as f:
        f.write(json.dumps(s, ensure_ascii=False) + "\n")
    brief = {k: v for k, v in s.items() if k not in ("wrong", "rows")}
    brief["wrong_n"] = [w["n"] for w in s.get("wrong", [])]
    print(json.dumps(brief, ensure_ascii=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["batch", "single", "big"])
    ap.add_argument("--reps", type=int, default=5)
    a = ap.parse_args()
    {"batch": lambda: cmd_batch(a.reps), "single": cmd_single, "big": cmd_big}[a.mode]()
