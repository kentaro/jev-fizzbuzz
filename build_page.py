"""results/*.jsonl から可視化ページ index.html を作る。数字はすべて実測ログから転記する。"""
import json
import pathlib

ROOT = pathlib.Path(__file__).parent
R = ROOT / "results"


def jl(name):
    return [json.loads(l) for l in open(R / name)]


batch = [b for b in jl("batch.jsonl") if b.get("status") == 200]
grid = next(b for b in reversed(batch) if "rows" in b)
single = jl("single.jsonl")[-1]
ladder = [x for x in jl("ladder.jsonl") if x["status"] == 200]

steps = []
for x in ladder:
    it = x["items"]
    steps.append({"digits": x["digits"], "ms": x["ms"], "n": len(it),
                  "fizzbuzz": sum(i["ok"] for i in it), "div3": sum(i["ok3"] for i in it),
                  "div5": sum(i["ok5"] for i in it),
                  "items": [{k: i[k] for k in ("n", "p3", "p5", "got", "want")} for i in it]})

data = {
    "grid": grid["rows"],
    "grid_ms": grid["ms"][0],
    "batch_ms": [b["ms"][0] for b in batch],
    "single": {"wall_ms": single["wall_ms"], "p50": single["p50"], "p95": single["p95"], "acc": single["fizzbuzz_acc"]},
    "steps": steps,
}

tpl = (ROOT / "page.tpl.html").read_text()
(ROOT / "index.html").write_text(tpl.replace("/*DATA*/null", json.dumps(data, ensure_ascii=False)))
print("wrote index.html", [(s["digits"], s["fizzbuzz"], s["n"]) for s in steps])

og = (ROOT / "og.tpl.html").read_text().replace("/*DATA*/null", json.dumps({"steps": steps}, ensure_ascii=False))
(ROOT / "og.html").write_text(og)
print("wrote og.html（headless Chrome で 1200x630 の og.png にする）")
