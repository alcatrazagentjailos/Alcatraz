#!/usr/bin/env python3
"""Test script for rate limiting using run_agent from alcatraz_step5.py
Runs an agent that calls TOOLS.bankr_prompt multiple times in the same agent process.
"""
from alcatraz_step5 import run_agent

AGENT_CODE = r'''
def run(TASK, TOOLS):
    out = []
    r1 = TOOLS.bankr_prompt("What is the price of ETH on Base?")
    out.append(r1)
    r2 = TOOLS.bankr_prompt("What is the price of ETH on Base?")
    out.append(r2)
    r3 = TOOLS.bankr_prompt("What is the price of ETH on Base?")
    out.append(r3)
    r4 = TOOLS.bankr_prompt("What is the price of ETH on Base?")
    out.append(r4)
    r5 = TOOLS.bankr_prompt("What is the price of ETH on Base?")
    out.append(r5)
    r6 = TOOLS.bankr_prompt("What is the price of ETH on Base?")
    out.append(r6)
    r7 = TOOLS.bankr_prompt("What is the price of ETH on Base?")
    out.append(r7)
    return out
'''

if __name__ == '__main__':
    result = run_agent(
        AGENT_CODE,
        grants=[
            ("bankr.use", 60, {
                "blocked_actions": ["transfer", "withdraw", "approve", "bridge"],
                "max_calls_per_min": 5,
                "poll_timeout_s": 60,
                "allowed_chains": ["base"],
                "max_usd": 101,
            })
        ],
    )

    print('RATE-LIMIT TEST RESULT:')
    import json
    print(json.dumps(result, indent=2))
