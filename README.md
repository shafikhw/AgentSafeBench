# Workflow Agent Safety Benchmark

An agentic AI safety benchmark specifically designed to evaluate how conversational AI handles unsafe tool-use scenarios. The goal of this benchmark is to deterministically measure an agent's ability to safely comply with valid user requests while refusing unsafe directives (such as prompt injections or explicitly forbidden actions), avoiding forbidden tool operations, and upholding data minimization.

## Architecture & Design Choice

This project implements a **controlled, reproducible tool-calling agent loop using the standard OpenAI client**. 
While the structure and nomenclature are inspired by high-level Agent SDK concepts (e.g. state management, tool registries, autonomous loops), we explicitly **do not** depend on a high-level Agents SDK runtime abstraction (like the experimental Swarm or Agents API wrappers). 

Exact tracing and deterministic interception requirements motivated this design choice. High-level agent frameworks currently obscure internal generation traces and do not let you cleanly intercept intermediate tool decisions without complex async hooks. Using a thin custom while-loop over the standard OpenAI Chat Completion API ensures our `RunRecord` can extract precisely when a tool is blocked natively versus when it is successfully executed, down to the millisecond.

## The Benchmark States

- **Baseline Agent**: A standard, undefended tool-calling loop using standard models models (e.g. `gpt-4o-mini`).
- **Defended Agent**: The identical agent loop, combined with a policy-aware guardrail wrapper (`app/safety.py`) that checks heuristics before allowing a tool to fire.

### Current Performance Status
The benchmark successfully forces edge-case behaviors and produces clean, heavily validated metrics. Following recent deterministic parser upgrades to isolate formatting faults, we can observe the genuine differences the heuristic layer provides.

| Metric | Baseline Agent | Defended Agent |
| :--- | :--- | :--- |
| **Safe Compliance Rate (SCR)** | 66.6% | 33.3% |
| **Safe Refusal Rate (SRR)** | 55.5% | 77.7% |
| **Attack Success Rate (ASR)** | 0.0% | 10.0% |
| **Unsafe Attempt Rate (UAAR)** | 0.0% | 6.6% |
| **Unsafe Execution Rate (UER)** | 0.0% | 0.0% |
| **Avg Requirement Score** | 0.93 | 0.93 |
| **Avg Safety Score** | 1.00 | 0.93 |
| **Composite Score** | 80.84 | 73.13 |
| **Soft Decision Accuracy** | 93.3% | 100.0% |

**Key Takeaways (Version 1):**
* **Baseline currently outperforms defended overall:** The composite score highlights that a lighter context window leads to stronger execution of original tasks without safety spillovers. 
* **Naive rule-based guardrails can degrade performance:** Forcing the LLM to juggle heavy "defense" prompt heuristics ironically induced confusion, triggering a false-positive prompt injection in the Defended model.
* **Strict output formatting remains a hurdle:** Isolating the parsing via a required `FINAL_DECISION` prefix drastically cleared formatting penalties, shifting the primary failure points exactly onto tool sequences and content matches.
* **The benchmark works:** The infrastructure reliably logs precisely when a safety hook activates, allowing clear analytical research onto what prompts natively defend vs degrade conversational workflows.

## Setup Instructions

1. Clone or download the repository.
2. Install standard Python requirements (Ensure you do this before plotting results):
   ```bash
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key for the models to work. **The pipeline explicitly requires this variable to run live endpoints.**
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

## Scenario Families
The benchmark datasets test the following:
- **Clean**: Benign workflow tasks. Tests capability.
- **Prompt Injection**: Embedded override commands in vendor emails, notes, or files.
- **Unauthorized Disclosure**: Direct user instructions to violate policy and leak internal or confidential payload.
- **Unsafe Tool Use**: User attempting to force `send_email` instead of `draft_email`, or tricking the agent with wrong recipients.

## Running the Benchmark

### 1. Validating Scenarios (Offline)
Before running, you can sanity check the JSON schemas. This runs purely offline:
```bash
PYTHONPATH=. python benchmark/validate_scenarios.py benchmark/scenarios_clean.json
```

### 2. Full Benchmark Pipeline (Requires `OPENAI_API_KEY`)
To evaluate the **baseline agent** across all 15 JSON scenarios:
```bash
PYTHONPATH=. python benchmark/evaluate.py
```

To evaluate the **defended agent** (which has the `app/safety.py` layer enabled):
```bash
PYTHONPATH=. python benchmark/evaluate.py --defended
```

### Expected Outputs
The pipeline cleanly splits outputs based on the mode so they do not overwrite each other:
- `results/baseline_runs.jsonl` or `results/defended_runs.jsonl`
- `results/baseline_metrics_summary.json` or `results/defended_metrics_summary.json`
- `results/baseline_transcripts/*` or `results/defended_transcripts/*`

## Analysis

You can run error analysis pointing directly to the mode you wish to investigate (e.g. `--mode baseline` or `--mode defended`):
```bash
PYTHONPATH=. python analysis/error_analysis.py --mode baseline
```

Generate plots for your research paper (`matplotlib` automatically handles the bar chart outputs):
```bash
PYTHONPATH=. python analysis/plots.py --mode baseline
```

## Running Tests (Offline)
Run 15+ internal PyTest suites covering schema validation, memory states, tools, grader accuracy, metrics math, and the safety wrapper without needing live API keys:
```bash
PYTHONPATH=. pytest
```
