"""results/*.jsonl から可視化ページ index.html を作る。数字はすべて実測ログから転記する。"""
import json
import pathlib

ROOT = pathlib.Path(__file__).parent
R = ROOT / "results"


def jl(name):
    return [json.loads(l) for l in open(R / name)]


batch = [b for b in jl("batch.jsonl") if b.get("status") == 200]
grid = next(b for b in reversed(batch) if "rows" in b)
single = next(s for s in reversed(jl("single.jsonl")))
ladder = jl("ladder.jsonl")

cells = {}
for rec in ladder:
    for it in rec["items"]:
        c = cells.setdefault(f'{rec["digits"]}_{it["d"]}', [0, 0])
        c[0] += it["ok"]
        c[1] += 1

examples = []
r20 = next(x for x in ladder if x["digits"] == 20)
for it in r20["items"]:
    if it["d"] == 3 and not it["ok"] and len(examples) < 4:
        examples.append({"n": it["n"], "p": it["p"], "truth": it["truth"], "digitsum": sum(map(int, it["n"]))})
r6 = next(x for x in ladder if x["digits"] == 6)
d11 = [it for it in r6["items"] if it["d"] == 11]

data = {
    "grid": grid["rows"],
    "grid_ms": grid["ms"][0],
    "batch_ms": [b["ms"][0] for b in batch],
    "single": {"wall_ms": single["wall_ms"], "p50": single["p50"], "p95": single["p95"], "acc": single["fizzbuzz_acc"]},
    "digits": [x["digits"] for x in ladder],
    "cells": cells,
    "ladder_ms": {x["digits"]: x["ms"] for x in ladder},
    "examples": examples,
    "d11_6": {"yes_said": sum(it["p"] >= 0.5 for it in d11), "total": len(d11),
              "divisible": sum(it["truth"] for it in d11)},
}

tpl = (ROOT / "page.tpl.html").read_text()
(ROOT / "index.html").write_text(tpl.replace("/*DATA*/null", json.dumps(data, ensure_ascii=False)))
print("wrote index.html", {k: (v if not isinstance(v, (list, dict)) else len(v)) for k, v in data.items()})
