import os
import json
import time
import urllib.request
import urllib.error
from typing import Optional

# ------------------------------
# POLICY / JAIL RULES
# ------------------------------
POLICY = {
    "allowed_actions": ["price", "balance", "swap"],
    "blocked_actions": ["transfer", "withdraw", "approve", "bridge"],
    "allowed_chains": ["base", "solana"],
    "max_usd": 101,
    "max_calls_per_min": 10,
    "poll_timeout_s": 60,
}

# ------------------------------
# KILL SWITCH
# ------------------------------
class KillSwitch(Exception):
    pass

def kill(reason):
    print(f"\n❌ AGENT KILLED → {reason}")
    raise KillSwitch(reason)

# ------------------------------
# AUDIT LOGGER
# ------------------------------
def audit(event, **data):
    print(f"[AUDIT] {event} | {data}")

# ------------------------------
# TOOL GATE (JAILED BANKR)
# ------------------------------
class ToolGate:
    def __init__(self):
        self.calls = []

    def _rate_limit(self):
        now = time.time()
        self.calls = [t for t in self.calls if now - t < 60]
        if len(self.calls) >= POLICY["max_calls_per_min"]:
            audit("tool_denied", reason="rate_limit")
            kill("RATE_LIMIT")
        self.calls.append(now)

    def _bankr_http(self, method, url, body=None):
        api_key = os.environ.get("BANKR_API_KEY")
        if not api_key:
            kill("BANKR_API_KEY_MISSING")
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={"Content-Type": "application/json", "X-API-Key": api_key},
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                raw = r.read().decode()
                return json.loads(raw) if raw else {}
        except Exception as e:
            kill(f"BANKR_HTTP_ERROR {e}")

    def bankr_prompt(self, prompt: str):
        audit("tool_attempt", prompt=prompt)
        self._rate_limit()

        p = prompt.lower()

        # BLOCKED ACTIONS
        for b in POLICY["blocked_actions"]:
            if b in p:
                audit("blocked_action", action=b)
                kill("BLOCKED_ACTION")

        # ACTION DETECTION
        action = "price"
        if "balance" in p:
            action = "balance"
        if any(x in p for x in ["swap", "buy", "sell"]):
            action = "swap"

        if action not in POLICY["allowed_actions"]:
            audit("action_not_allowed", action=action)
            kill("ACTION_NOT_ALLOWED")

        # USD LIMIT
        for word in p.split():
            if word.startswith("$"):
                try:
                    amount = float(word[1:])
                    if amount > POLICY["max_usd"]:
                        audit("max_usd_exceeded", amount=amount)
                        kill("MAX_USD_EXCEEDED")
                except:
                    pass

        # CHAIN CHECK
        for ch in ["ethereum", "polygon", "base", "solana"]:
            if ch in p and ch not in POLICY["allowed_chains"]:
                audit("chain_not_allowed", chain=ch)
                kill("CHAIN_NOT_ALLOWED")

        # SEND TO BANKR
        submit = self._bankr_http(
            "POST",
            "https://api.bankr.bot/agent/prompt",
            {"prompt": prompt},
        )

        job_id = submit.get("jobId")
        if not job_id:
            kill("NO_JOB_ID")

        start = time.time()
        while True:
            if time.time() - start > POLICY["poll_timeout_s"]:
                kill("POLL_TIMEOUT")

            job = self._bankr_http(
                "GET",
                f"https://api.bankr.bot/agent/job/{job_id}",
            )

            status = job.get("status")
            audit("job_poll", status=status)

            if status == "completed":
                txs = job.get("transactions", [])
                for t in txs:
                    ttype = (t or {}).get("type", "")
                    if any(x in ttype for x in POLICY["blocked_actions"]):
                        audit("blocked_tx", tx=ttype)
                        kill("BLOCKED_TX_TYPE")
                return job

            if status in ["failed", "cancelled"]:
                kill(f"JOB_{status.upper()}")

            time.sleep(2)

# ------------------------------
# AGENT (JAILED)
# ------------------------------
def agent():
    tools = ToolGate()

    # ✅ SAFE PROMPT EXAMPLE
    result = tools.bankr_prompt("What is the price of ETH on base?")

    print("\n✅ AGENT RESULT:")
    print(json.dumps(result, indent=2))

# ------------------------------
# RUN
# ------------------------------
if __name__ == "__main__":
    try:
        agent()
    except KillSwitch:
        pass
