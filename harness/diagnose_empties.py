#!/usr/bin/env python3
"""Re-issue specific HumanEval tasks against a running llama-server and report
whether they come back EMPTY.

Why: an empty completion is scored as a wrong answer (issue #7). When a run happens
on a contended box, we need to know whether its empties were caused by the model or
by the machine. Re-issuing the same tasks on a QUIET box answers that directly.

Replicates evalplus/provider/openai.py exactly:
  message = instruction_prefix + "\\n```python\\n" + prompt.strip() + "\\n```"
  chat.completions, temperature 0.0, max_tokens 4096, n=1

Usage: diagnose_empties.py <port> <task_id> [task_id ...]
"""
import sys, json, urllib.request

PREFIX = ("Please provide a self-contained Python script that solves the following "
          "problem in a markdown code block:")

def main():
    port = sys.argv[1]; tasks = sys.argv[2:]
    from evalplus.data import get_human_eval_plus
    probs = get_human_eval_plus()
    url = f"http://127.0.0.1:{port}/v1/chat/completions"
    print(f"{'task':16s} {'chars':>7s}  verdict")
    print("-"*40)
    results = {}
    for t in tasks:
        prompt = probs[t]["prompt"]
        msg = PREFIX + f"\n```python\n{prompt.strip()}\n```"
        body = json.dumps({"model": "local", "messages": [{"role": "user", "content": msg}],
                           "temperature": 0.0, "max_tokens": 4096, "n": 1}).encode()
        req = urllib.request.Request(url, data=body,
                                     headers={"Content-Type": "application/json",
                                              "Authorization": "Bearer dummy"})
        try:
            with urllib.request.urlopen(req, timeout=1800) as r:
                out = json.load(r)["choices"][0]["message"]["content"] or ""
        except Exception as e:
            out = ""; print(f"{t:16s} {'ERR':>7s}  {type(e).__name__}: {e}")
            results[t] = None; continue
        n = len(out.strip())
        results[t] = n
        print(f"{t:16s} {n:7d}  {'EMPTY' if n == 0 else 'produced output'}")
    print("-"*40)
    empt = [t for t, v in results.items() if v == 0]
    print(f"still empty on a quiet box: {len(empt)}/{len(tasks)}  {empt}")
    json.dump(results, open("/tmp/diagnose_empties.json", "w"), indent=2)

if __name__ == "__main__":
    main()
