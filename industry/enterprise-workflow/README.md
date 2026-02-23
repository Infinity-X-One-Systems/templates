# Enterprise Workflow Engine

A production-grade Python module for defining, executing, and analyzing multi-step approval workflows with designated approvers.

## Features
- Define workflows with ordered steps and approvers
- Create and track workflow instances
- Advance steps with approval or rejection logic
- Identify process bottlenecks via duration analysis
- Calculate workflow completion rates

## Usage
```python
from src.engine import EnterpriseWorkflowEngine

engine = EnterpriseWorkflowEngine()
wf = engine.define_workflow("Budget Approval", ["Draft", "Review", "Approve"], ["manager", "director", "cfo"])
inst = engine.create_instance(wf.id, "requester", {"amount": 10000})
inst = engine.advance_step(inst.id, "manager", True, "Looks reasonable")
```
