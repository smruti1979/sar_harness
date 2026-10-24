"""
Compare providers over many random worlds.

  python benchmark.py                                         # mock only, 10 seeds
  python benchmark.py --providers mock openai --seeds 10
  python benchmark.py --providers mock gullible quitter --seeds 10 --inject   # guard stress test
  python benchmark.py --providers openai --seeds 5 --per-seed # one line per run, with final text

Each seed gives a different hidden subject location. `found` is verified by the harness,
not taken from the model's own claim. Real providers cost money: start with few seeds.
"""
import argparse, os, statistics
import sar_harness as sar

def run_one(provider, seed, inject):
    sar.LOG_FILE = os.devnull                      # don't write logs during benchmarks
    world = sar.World(seed)
    tools = sar.make_tools(world, inject=inject)
    system = sar.build_system_prompt(tools)
    llm = sar.make_llm(provider, system)
    return sar.run_agent(llm, tools, system, "Begin the search.", verbose=False, world=world)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--providers", nargs="+", default=["mock"])
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--inject", action="store_true", help="add the malicious report to every run")
    ap.add_argument("--per-seed", action="store_true", help="print one line per run")
    a = ap.parse_args()

    print(f"{a.seeds} seeds | injection: {'ON' if a.inject else 'off'} | max steps {sar.MAX_STEPS} "
          f"| POS target {sar.POS_TARGET:.0%}\n")
    print(f"{'provider':<10} {'found':>7} {'avg disp*':>10} {'avg POS':>8} {'escalated':>10} "
          f"{'guard hits':>11} {'api errors':>11}")
    for provider in a.providers:
        runs, errors = [], 0
        for seed in range(1, a.seeds + 1):
            try:
                r = run_one(provider, seed, a.inject)
                runs.append(r)
                if a.per_seed:
                    print(f"  {provider} seed {seed}: found={r['found']} outcome={r['outcome']} "
                          f"dispatches={r['dispatches']} POS={r['pos']:.0%} {r['stats']}")
                    print(f"      final: {r['final'][:110]}")
            except Exception as e:
                errors += 1
                print(f"  {provider} seed {seed}: ERROR {type(e).__name__}: {e}")
        if not runs:
            print(f"{provider:<10} (no successful runs)")
            continue
        found = [r for r in runs if r["found"]]
        avg = statistics.mean(r["dispatches"] for r in found) if found else float("nan")
        avg_pos = statistics.mean(r["pos"] for r in runs)
        esc = sum(r["outcome"] == "escalated" for r in runs)
        guards = sum(v for r in runs for k, v in r["stats"].items() if k not in ("dispatches", "steps"))
        print(f"{provider:<10} {len(found):>3}/{len(runs):<3} {avg:>10.1f} {avg_pos:>8.0%} {esc:>10} "
              f"{guards:>11} {errors:>11}")
    print("\n* average dispatches over runs where the subject was actually found")

if __name__ == "__main__":
    main()
