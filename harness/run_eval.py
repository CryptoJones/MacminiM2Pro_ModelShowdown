#!/usr/bin/env python3
"""Executable coding eval. Hits an OpenAI-compatible /v1/chat/completions endpoint,
extracts the Python function, runs hidden unit tests in an isolated subprocess, scores pass@1."""
import argparse, json, re, subprocess, sys, time, urllib.request, tempfile, os
from problems import PROBLEMS

SYS = ("You are an expert Python programmer. Respond with exactly ONE Python function "
       "in a single ```python code block. No prose, no examples, no tests.")

def chat(base, model, prompt, max_tokens, temp, timeout=600):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": SYS}, {"role": "user", "content": prompt}],
        "temperature": temp, "max_tokens": max_tokens, "stream": False,
    }).encode()
    req = urllib.request.Request(base.rstrip("/") + "/v1/chat/completions", data=body,
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer x"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.load(r)
    dt = time.time() - t0
    content = d["choices"][0]["message"]["content"]
    usage = d.get("usage", {})
    return content, dt, usage

def extract_code(text):
    # strip <think>...</think> reasoning blocks first
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    m = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, flags=re.DOTALL)
    if m:
        # pick the longest fenced block (the actual function)
        return max(m, key=len)
    return text  # fallback: whole content

def run_test(code, test, timeout=20):
    src = code + "\n\n" + test + "\nprint('OK')\n"
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(src); path = f.name
    try:
        p = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=timeout)
        ok = p.returncode == 0 and p.stdout.strip().endswith("OK")
        err = "" if ok else (p.stderr.strip().splitlines()[-1] if p.stderr.strip() else "no-OK")
        return ok, err
    except subprocess.TimeoutExpired:
        return False, "timeout"
    finally:
        os.unlink(path)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--temp", type=float, default=0.0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--limit", type=int, default=0, help="only run first N problems (0=all)")
    a = ap.parse_args()

    probs = PROBLEMS[:a.limit] if a.limit else PROBLEMS
    results, npass, gen_toks, gen_time = [], 0, 0, 0.0
    for prob in probs:
        try:
            content, dt, usage = chat(a.base_url, a.model, prob["prompt"], a.max_tokens, a.temp)
        except Exception as e:
            results.append({"id": prob["id"], "pass": False, "err": f"api:{e}"});
            print(f"  {prob['id']:24s} ERR api {e}"); continue
        code = extract_code(content)
        ok, err = run_test(code, prob["test"])
        npass += int(ok)
        ct = usage.get("completion_tokens", 0); gen_toks += ct; gen_time += dt
        results.append({"id": prob["id"], "pass": ok, "err": err, "sec": round(dt,2), "ctoks": ct})
        print(f"  {prob['id']:24s} {'PASS' if ok else 'FAIL '+err[:50]}  ({dt:.1f}s, {ct}tok)")

    n = len(probs)
    tps = (gen_toks / gen_time) if gen_time else 0
    summary = {"label": a.label, "model": a.model, "pass": npass, "total": n,
               "pass_at_1": round(npass / n, 3), "approx_gen_tps": round(tps, 1),
               "results": results}
    print(f"\n=== {a.label}: pass@1 = {npass}/{n} = {npass/n:.1%}  | approx {tps:.1f} tok/s (API wall-clock) ===")
    if a.out:
        with open(a.out, "w") as f: json.dump(summary, f, indent=2)
        print(f"wrote {a.out}")

if __name__ == "__main__":
    main()
