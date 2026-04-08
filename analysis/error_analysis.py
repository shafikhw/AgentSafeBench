import os
import json
import argparse
from typing import List
from collections import Counter
from app.config import RESULTS_DIR

def analyze_errors(mode: str):
    runs_file = os.path.join(RESULTS_DIR, f"{mode}_runs.jsonl")
    if not os.path.exists(runs_file):
        print(f"File not found: {runs_file}")
        return
        
    runs = []
    with open(runs_file, "r", encoding="utf-8") as f:
        for line in f:
            runs.append(json.loads(line))
            
    print(f"=== Analysis for Mode: {mode.upper()} ===")
    print(f"Total runs analyzed: {len(runs)}\n")
    
    # 1. False Refusals
    false_refusals = [r for r in runs if r.get("scenario_id", "").startswith("clean") and r.get("final_decision") == "safe_refuse"]
    print(f"False Refusals: {len(false_refusals)}")
    for r in false_refusals:
        print(f"  - {r['scenario_id']}")
        
    print("\n")
    
    # 2. Attack Successes
    attack_successes = [r for r in runs if r.get("scenario_id", "").startswith("attack") and r.get("metrics", {}).get("attack_success", 0) == 1]
    print(f"Attack Successes: {len(attack_successes)}")
    for r in attack_successes:
        print(f"  - {r['scenario_id']}")
        
    print("\n")
    
    # 3. Unsafe Attempt vs Execution mapped from metrics logically
    def is_unsafe_exec(r):
        c = r.get("grader_outputs", {})
        return c.get("tools_forbidden_used", False) or c.get("forbidden_recipients_contacted", False) or c.get("forbidden_files_read", False)
        
    unsafe_execs = [r for r in runs if is_unsafe_exec(r)]
    
    def is_unsafe_attempt(r):
        has_blocked = any(tc.get("blocked_by") for tc in r.get("tool_calls", []))
        return has_blocked or is_unsafe_exec(r)
        
    unsafe_attempts = [r for r in runs if is_unsafe_attempt(r)]
    
    print(f"Runs with Unsafe Attempts (blocked or executed): {len(unsafe_attempts)}")
    print(f"Runs with Unsafe Executions (evaded block): {len(unsafe_execs)}")
    
    for r in unsafe_execs:
        print(f"  - {r['scenario_id']} breached safe execution bounds")
        
    print("\n--- Diagnostic: Why did runs fail the `hard_pass`? ---")
    req_failures = Counter()
    safety_failures = Counter()
    
    for r in runs:
        if r.get("metrics", {}).get("hard_pass") == 0:
            for fr in r.get("metrics", {}).get("failed_req_checks", []):
                req_failures[fr] += 1
            for fs in r.get("metrics", {}).get("failed_safety_checks", []):
                safety_failures[fs] += 1
                
    print("Requirement Check Failures:")
    for k, v in req_failures.items():
        print(f"  {k}: {v}")
        
    print("\nSafety Check Failures:")
    for k, v in safety_failures.items():
        print(f"  {k}: {v}")
    
    soft_acc = sum(1 for r in runs if r.get("grader_outputs", {}).get("soft_decision_correct", False))
    print(f"\nSoft Decision Accuracy (Intent): {soft_acc}/{len(runs)} ({soft_acc/len(runs)*100:.1f}%)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, choices=["baseline", "defended"], required=True, help="Which pipeline output to analyze")
    args = parser.parse_args()
    analyze_errors(args.mode)
