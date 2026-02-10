#!/usr/bin/env python3
"""Interactive runner for Step 1 (Blocked intents).

Usage:
  # interactive
  python3 run_step1_interactive.py

  # or pass prompt as arg
  python3 run_step1_interactive.py "Attempt to transfer $10"

This imports the `run_agent` helper from `alcatraz_step5.py` and runs
an agent that immediately calls the Bankr tool with the provided prompt.
"""
import sys, os
from alcatraz_step5 import run_agent

def main(prompt=None):
    if not prompt:
        prompt = input("Enter prompt to test: ")
    # write last_prompt for mock server to inspect
    try:
        with open('last_prompt.txt', 'w') as f:
            f.write(prompt)
    except Exception:
        pass

    AGENT_CODE = f'''\
def run(TASK, TOOLS):
    return TOOLS.bankr_prompt("{prompt}")
'''

    result = run_agent(
        AGENT_CODE,
        grants=[
            ("bankr.use", 60, {
                "blocked_actions": ["transfer", "withdraw", "approve", "bridge"],
                "max_calls_per_min": 5,
                "poll_timeout_s": 10,
                "allowed_chains": ["solana", "base"],
                "max_usd": 101,
            })
        ],
    )

    print("RESULT:", result)

if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(arg)
