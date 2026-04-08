import os
import json
import matplotlib.pyplot as plt
import argparse

def create_plots(mode: str):
    summary_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", f"{mode}_metrics_summary.json")
    if not os.path.exists(summary_file):
        print(f"Summary file not found for mode: {mode}")
        return
        
    with open(summary_file, "r", encoding="utf-8") as f:
        metrics = json.load(f)
        
    labels = ["SCR", "SRR", "1 - FRR", "1 - ASR"]
    values = [
        metrics.get("scr", 0) * 100,
        metrics.get("srr", 0) * 100,
        (1 - metrics.get("frr", 0)) * 100,
        (1 - metrics.get("asr", 0)) * 100
    ]
    
    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color=["green", "blue", "orange", "red"])
    plt.ylim(0, 100)
    plt.title(f"Key Safety Metrics: {mode.upper()}")
    plt.ylabel("Percentage (%)")
    
    for i, v in enumerate(values):
        plt.text(i, v + 2, f"{v:.1f}%", ha='center')
        
    out_path = summary_file.replace(".json", "_plot.png")
    plt.savefig(out_path)
    print(f"Plot saved to: {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, choices=["baseline", "defended"], required=True, help="Which pipeline plot to generate")
    args = parser.parse_args()
    create_plots(args.mode)
