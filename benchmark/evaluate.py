import os
import sys
import json
import argparse
from typing import List

from benchmark.loader import load_all_scenarios
from app.agent import WorkflowSafetyAgent
from app.runner import run_scenario
from benchmark.graders import grade_run
from benchmark.metrics import compute_metrics
from app.config import RESULTS_DIR, TRANSCRIPTS_DIR
from dotenv import load_dotenv

def check_preflight():
    load_dotenv()
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n\n" + "="*60)
        print("ERROR: Missing OPENAI_API_KEY environment variable.")
        print("The benchmark evaluates the underlying model through the OpenAI SDK.")
        print("Please export your API key before running the evaluation pipeline:")
        print("  export OPENAI_API_KEY='sk-...'")
        print("="*60 + "\n\n")
        sys.exit(1)

def setup_directories(prefix: str):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    ts_dir = os.path.join(TRANSCRIPTS_DIR, prefix)
    os.makedirs(ts_dir, exist_ok=True)
    return ts_dir

def main():
    parser = argparse.ArgumentParser(description="Run the Workflow Safety Benchmark.")
    parser.add_argument("--scenarios_dir", type=str, default="benchmark", help="Directory containing scenarios")
    parser.add_argument("--mode", type=str, choices=["baseline", "defended"], default="baseline", help="Run the baseline or defended agent")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="OpenAI model to use")
    
    args = parser.parse_args()
    check_preflight()
    
    prefix = args.mode
    is_defended = prefix == "defended"
    ts_dir = setup_directories(prefix)
    
    scenarios = load_all_scenarios(args.scenarios_dir)
    if not scenarios:
        print("No scenarios found!")
        return
        
    print(f"Loaded {len(scenarios)} scenarios.")
    
    agent = WorkflowSafetyAgent(model=args.model, use_safety=is_defended)
    scenarios_dict = {s.id: s for s in scenarios}
    
    records = []
    
    run_log_path = os.path.join(RESULTS_DIR, f"{prefix}_runs.jsonl")
    with open(run_log_path, "w", encoding="utf-8") as f:
        pass # Clear existing file
    
    for idx, scenario in enumerate(scenarios):
        print(f"[{idx+1}/{len(scenarios)}] Running Scenario: {scenario.id} - {scenario.title}")
        
        # Run
        record = run_scenario(scenario, agent)
        
        # Grade
        grader_dict = grade_run(record, scenario)
        
        # Attach metrics
        record.grader_outputs = grader_dict["checks"]
        metrics_dict = {
            "req_passed": grader_dict["req_passed"],
            "req_total": grader_dict["req_total"],
            "safety_penalty": grader_dict["safety_penalty"],
            "total_safety_penalty": grader_dict["total_safety_penalty"],
            "req_score": grader_dict["req_score"],
            "safety_score": grader_dict["safety_score"],
            "attack_success": grader_dict["attack_success"],
            "efficiency_score": grader_dict["efficiency_score"],
            "scenario_score": grader_dict["scenario_score"],
            "hard_pass": grader_dict["hard_pass"],
            "failed_req_checks": grader_dict["failed_req_checks"],
            "failed_safety_checks": grader_dict["failed_safety_checks"]
        }
        record.metrics = metrics_dict
        
        records.append(record)
        
        # Dump to JSONL
        with open(run_log_path, "a", encoding="utf-8") as f:
            f.write(record.model_dump_json() + "\n")
            
        # Dump transcript
        ts_path = os.path.join(ts_dir, f"{record.run_id}_{record.scenario_id}.json")
        with open(ts_path, "w", encoding="utf-8") as f:
            f.write(record.model_dump_json(indent=2))
            
    # Compute aggregate metrics
    metrics = compute_metrics(records, scenarios_dict)
    
    # Save overall summary
    summary_path = os.path.join(RESULTS_DIR, f"{prefix}_metrics_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(metrics.model_dump_json(indent=2))
        
    print(f"\nBenchmark Complete! Mode: {prefix.upper()}")
    print(f"Results written to: {run_log_path}")
    print(metrics.model_dump_json(indent=2))
    
if __name__ == "__main__":
    main()
