import subprocess, random, string, time, os, json

# 🧠 Simple “fuzz” generator
def random_text(length=20):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

def run_once(script, args):
    """Run one test iteration and record output."""
    try:
        cmd = ["python", script] + args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return {"args": args, "stdout": result.stdout[:300], "stderr": result.stderr[:300], "rc": result.returncode}
    except Exception as e:
        return {"args": args, "error": str(e)}

# 🔁 Loop for many iterations
def main():
    target = "leviathan/utils.py"      # pick one main module to start
    results = []
    for i in range(1000):              # run 1000 iterations
        args = [random_text(5), random_text(10)]
        print(f"🔍 Test {i+1}/1000 with args={args}")
        results.append(run_once(target, args))
        time.sleep(0.05)               # small pause so your PC can breathe

    # save results
    os.makedirs("exports/fuzz_logs", exist_ok=True)
    with open("exports/fuzz_logs/results.json", "w", encoding="utf8") as f:
        json.dump(results, f, indent=2)
    print("✅ Done. Results saved in exports/fuzz_logs/results.json")

if __name__ == "__main__":
    main()
