import os
import argparse
from pydantic import ValidationError
from benchmark.loader import load_scenarios

def main():
    parser = argparse.ArgumentParser(description="Validate JSON scenarios against schema.")
    parser.add_argument("file", help="Path to the JSON file to validate")
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File {args.file} not found.")
        exit(1)
        
    try:
        scenarios = load_scenarios(args.file)
        print(f"SUCCESS: {args.file} passed validation. Loaded {len(scenarios)} scenarios.")
    except ValidationError as e:
        print(f"VALIDATION FAILED for {args.file}")
        print(e)
        exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)

if __name__ == "__main__":
    main()
