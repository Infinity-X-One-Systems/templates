# Autonomous Loop

An OODA-based (Observe → Orient → Decide → Act) autonomous agent loop with hard governance limits.
Enforces cost budget, iteration cap, and irreversible-action gating; escalates to human approval when needed.
Wire `execute_action` to real `connectors/` calls to deploy a live autonomous agent.
