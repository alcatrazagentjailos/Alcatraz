#!/usr/bin/env python3
from alcatraz_step2 import run_agent

AGENT_CODE = r'''
def run(TASK, TOOLS):
    out = []
    out.append(TOOLS.bankr_prompt("What is the price of ETH on Base?"))
    out.append(TOOLS.bankr_prompt("What is the price of ETH on Base?"))
    out.append(TOOLS.bankr_prompt("What is the price of ETH on Base?"))
    out.append(TOOLS.bankr_prompt("What is the price of ETH on Base?"))
    out.append(TOOLS.bankr_prompt("What is the price of ETH on Base?"))
    out.append(TOOLS.bankr_prompt("What is the price of ETH on Base?"))
    out.append(TOOLS.bankr_prompt("What is the price of ETH on Base?"))
    return out
'''

if __name__ == '__main__':
    result = run_agent(
        AGENT_CODE,
        grants=[
            ("bankr.use", 60, {
                "blocked_actions": ["transfer","withdraw","approve","bridge"],
                "max_calls_per_min": 5,
            })
        ],
    )
    import json
    print('STEP2 RATE TEST RESULT:')
    print(json.dumps(result, indent=2))
