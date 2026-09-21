# -*- coding: utf-8 -*-
"""Q5 tuning A/B stage 2 (054 s3.2): compare 2x14 / 2x7 / 3x5 / 3x4.

Why another driver: the 09-14 t005_ab.py wrote its report only after all four
configs, so the 09-18 attempt (a and b completed, c killed mid-flight) left no
usable numbers. This version rewrites t005_ab2_results.json after EVERY config,
samples per-core CPU (058 asks for per-core distribution), and caps each config
so a hung config cannot block the run forever.

- Synthetic random-walk load inside _ab2/ only; never touches locked data and
  never produces C1 results (A/B numbers must not enter the C1 evidence chain).
- Resumable: a config already present in the results JSON is skipped.
"""
import argparse, csv, datetime, json, os, random, subprocess, sys, threading, time

REPO = r"C:\Users\geng\DeReFusion"
PY = os.path.join(REPO, ".venv", "Scripts", "python.exe")
AB = os.path.join(REPO, "_ab2")
CSV_PATH = os.path.join(AB, "ABTEST-2016-2025.csv")
RESULTS = os.path.join(REPO, "t005_ab2_results.json")
REPORT = os.path.join(REPO, "t005_ab2_report.txt")
CONFIGS = [("a", 2, 14), ("b", 2, 7), ("c", 3, 5), ("d", 3, 4)]
CFG_CAP_MIN = 60.0
SAMPLE_S = 15

PS_SAMPLE = (r"Get-Counter '\Processor(*)\% Processor Time' -ErrorAction SilentlyContinue "
             r"| Select-Object -ExpandProperty CounterSamples "
             r"| ForEach-Object { $_.InstanceName + ':' + [math]::Round($_.CookedValue,1) }")


def gen_synthetic(rows=600):
    os.makedirs(AB, exist_ok=True)
    random.seed(20260914)
    px, d = 100.0, datetime.date(2016, 1, 4)
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "Open", "High", "Low", "Close"])
        for _ in range(rows):
            while d.weekday() >= 5:
                d += datetime.timedelta(days=1)
            o = px
            px = max(1.0, px * (1 + random.gauss(0, 0.012)))
            w.writerow([d.isoformat(), "%.6f" % o,
                        "%.6f" % (max(o, px) * (1 + abs(random.gauss(0, 0.004)))),
                        "%.6f" % (min(o, px) * (1 - abs(random.gauss(0, 0.004)))),
                        "%.6f" % px])
            d += datetime.timedelta(days=1)


class Sampler(threading.Thread):
    """Samples per-logical-core busy% in the background."""

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.rows = []
        # Never name this "_stop": Thread._stop() is a real method and join()
        # calls it -> "TypeError: 'bool' object is not callable" (2026-09-18 crash).
        self._halt = False

    def run(self):
        while not self._halt:
            try:
                r = subprocess.run(["powershell", "-NoProfile", "-Command", PS_SAMPLE],
                                   capture_output=True, text=True, timeout=SAMPLE_S * 3)
                d = {}
                for line in r.stdout.splitlines():
                    if ":" in line:
                        k, _, v = line.partition(":")
                        k = k.strip()
                        if k and k != "_Total":
                            try:
                                d[int(k)] = float(v)
                            except ValueError:
                                pass
                if d:
                    self.rows.append(d)
            except Exception:
                pass
            time.sleep(SAMPLE_S)

    def stop(self):
        self._halt = True


def run_config(tag, lanes, threads, epochs, cap_min):
    procs, logs = [], []
    started = datetime.datetime.now()
    t0 = time.time()
    for i in range(lanes):
        mid = "AB%s_p%d" % (tag, i)
        args = [PY, "run.py", "--task_name", "long_term_forecast", "--is_training", "1",
                "--model_id", mid, "--model", "DeReFusion", "--data", "custom",
                "--root_path", "./_ab2/", "--data_path", "ABTEST-2016-2025.csv",
                "--features", "MS", "--target", "Close", "--freq", "b",
                "--seq_len", "96", "--label_len", "48", "--pred_len", "24",
                "--enc_in", "4", "--dec_in", "4", "--c_out", "1",
                "--d_model", "32", "--moving_avg", "25",
                "--train_epochs", str(epochs), "--batch_size", "32", "--learning_rate", "0.0001",
                "--patience", "5", "--lradj", "cosine", "--rand_seed", "2021", "--no_use_gpu"]
        env = dict(os.environ, OMP_NUM_THREADS=str(threads), MKL_NUM_THREADS=str(threads),
                   PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        lg = open(os.path.join(AB, mid + ".out"), "w")
        procs.append(subprocess.Popen(args, cwd=REPO, env=env, stdout=lg,
                                      stderr=subprocess.STDOUT))
        logs.append(lg)
    smp = Sampler()
    smp.start()
    note = "ok"
    while any(p.poll() is None for p in procs):
        if (time.time() - t0) / 60.0 > cap_min:
            note = "CAPPED-AT-%dMIN" % int(cap_min)
            for p in procs:
                if p.poll() is None:
                    p.kill()
            break
        time.sleep(5)
    smp.stop()
    smp.join(timeout=10)
    for lg in logs:
        lg.close()
    wall = round((time.time() - t0) / 60.0, 2)
    ok = 0
    rd = os.path.join(REPO, "results")
    for i in range(lanes):
        pat = "long_term_forecast_AB%s_p%d_" % (tag, i)
        for d in os.listdir(rd):
            if d.startswith(pat) and os.path.exists(os.path.join(rd, d, "metrics.npy")):
                ok += 1
                break
    core = {}
    for row in smp.rows:
        for k, v in row.items():
            core.setdefault(k, []).append(v)
    core_mean = dict((str(k), round(sum(v) / len(v), 1))
                     for k, v in sorted(core.items()))
    idle = [k for k, v in core_mean.items() if v < 5.0]
    tot = round(sum(core_mean.values()) / len(core_mean), 1) if core_mean else None
    return {"tag": tag, "lanes": lanes, "threads": threads, "epochs": epochs,
            "ok": ok, "wall_min": wall,
            "runs_per_hour": round(ok / (wall / 60.0), 2) if wall > 0 else 0,
            "core_mean_pct": core_mean, "core_total_mean_pct": tot,
            "idle_cores_lt5pct": idle, "samples": len(smp.rows), "note": note,
            "startedAt": started.strftime("%Y-%m-%d %H:%M:%S"),
            "endedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


def write_report(res):
    L = ["=== T005 Q5 tuning A/B (stage 2, t005_ab2.py) ===",
         "load: synthetic random-walk CSV (600 rows) in _ab2/, model DeReFusion d_model=32, "
         "%d epochs" % res.get("epochs", 30),
         "NOT locked data and NOT C1 results: these numbers must never enter the C1 evidence chain",
         ""]
    L.append("%-8s %8s %10s %11s %11s  %s" % ("config", "runs ok", "wall_min",
                                              "runs/hour", "cpu tot%", "note"))
    for tag, lanes, threads in CONFIGS:
        r = res["configs"].get(tag)
        name = "%dx%d" % (lanes, threads)
        if not r:
            L.append("%-8s %8s %10s %11s %11s  %s" % (name, "-", "-", "-", "-", "pending"))
            continue
        L.append("%-8s %8d %10.2f %11.2f %11s  %s" % (
            name, r["ok"], r["wall_min"], r["runs_per_hour"],
            r["core_total_mean_pct"], r["note"]))
    L.append("")
    for tag, lanes, threads in CONFIGS:
        r = res["configs"].get(tag)
        if r and r.get("core_mean_pct"):
            name = "%dx%d" % (lanes, threads)
            L.append("%s per-core mean%%: %s" % (name, json.dumps(r["core_mean_pct"])))
            L.append("%s idle cores (<5%%): %s" % (name, r["idle_cores_lt5pct"]))
    L.append("")
    done = len(res["configs"]) == len(CONFIGS)
    L.append("status: %s" % ("COMPLETE" if done else
                             "IN-PROGRESS (%d/%d)" % (len(res["configs"]), len(CONFIGS))))
    L.append("updated: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    open(REPORT, "w", encoding="utf-8").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--cap", type=float, default=CFG_CAP_MIN)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--log", default="")
    a = ap.parse_args()

    if a.log:
        lf = open(os.path.join(REPO, a.log), "a", encoding="utf-8", buffering=1)

        class _Tee(object):
            def write(self, s):
                lf.write(s)

            def flush(self):
                lf.flush()

        sys.stdout = sys.stderr = _Tee()
        print("=== t005_ab2 detached start %s ===" %
              datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    cfgs = CONFIGS
    if a.smoke:
        cfgs = [("s", 2, 2)]
        a.epochs = 2
        a.cap = 8.0
    elif a.only:
        want = set(x.strip() for x in a.only.split(",") if x.strip())
        cfgs = [c for c in CONFIGS if c[0] in want]

    gen_synthetic()
    res = {"epochs": a.epochs, "cap_min": a.cap, "configs": {}}
    if os.path.exists(RESULTS) and not a.smoke:
        try:
            old = json.load(open(RESULTS, encoding="utf-8"))
            if old.get("epochs") == a.epochs:
                res["configs"] = old.get("configs", {})
        except Exception:
            pass
    open(RESULTS, "w", encoding="utf-8").write(json.dumps(res, indent=1))

    for tag, lanes, threads in cfgs:
        if tag in res["configs"]:
            continue
        print("config %dx%d (%s) start" % (lanes, threads, tag), flush=True)
        r = run_config(tag, lanes, threads, a.epochs, a.cap)
        res["configs"][tag] = r
        open(RESULTS, "w", encoding="utf-8").write(json.dumps(res, indent=1))
        write_report(res)
        print("config %dx%d done: ok=%d wall=%.2fmin rph=%.2f" % (
            lanes, threads, r["ok"], r["wall_min"], r["runs_per_hour"]), flush=True)

    write_report(res)
    print("RESULTS ->", RESULTS)
    print("REPORT  ->", REPORT)


if __name__ == "__main__":
    main()
