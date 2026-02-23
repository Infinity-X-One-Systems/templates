# Universal Pipeline Stages

The Infinity Template Library implements a universal 8-stage workflow pattern applicable to any business, product, or system. Every stage produces structured artifacts consumed by the next, forming a closed loop of continuous improvement.

## The 8-Stage Pattern

```
Discovery → Design → Build → Test → Deploy → Monitor → Optimize → Scale → (back to Discovery)
```

Each stage is defined by a `stage.json` contract under `stages/<name>/stage.json`. Stages can be wired into GitHub Actions jobs, triggered by webhooks, or orchestrated by the Infinity Admin Control Plane.

### Stage Descriptions

| Stage | Description |
|-------|-------------|
| **Discovery** | Capture requirements, constraints, stakeholders, and budget. Produces a system brief. |
| **Design** | Architect the system, select templates, generate the system manifest and architecture diagram. |
| **Build** | Scaffold all components from the manifest. Produces a generated repo and Docker images. |
| **Test** | Run tests, linting, type checks, and security scans. Gate on coverage and security thresholds. |
| **Deploy** | Deploy to sandbox first, validate, then promote to production with rollback plan. |
| **Monitor** | Continuously observe health, performance, errors, and costs via telemetry. |
| **Optimize** | Analyze telemetry and autonomously propose or apply improvements (governed). |
| **Scale** | Scale infrastructure and replicate proven patterns to new domains. |

## Stage Contract Table

| Stage | Trigger | Inputs | Outputs | GitHub Action Job |
|-------|---------|--------|---------|-------------------|
| discovery | manual \| webhook \| api | problem_statement, constraints, stakeholders, budget | system_brief, architecture_map, decision_log_entry | `discovery` |
| design | discovery_complete | system_brief, template_library, constraints | system_manifest, architecture_diagram, dependency_graph | `design` |
| build | design_complete | system_manifest, template_library | generated_repo, docker_images, api_stubs | `build` |
| test | build_complete | generated_repo | test_report, coverage_report, security_report | `test` |
| deploy | test_complete | generated_repo, test_report, security_report | sandbox_url, production_url, deployment_log | `deploy` |
| monitor | deploy_complete \| schedule(*/15 * * * *) | production_url, deployment_manifest | health_report, alert_list, telemetry_snapshot | `monitor` |
| optimize | monitor_alert \| schedule(0 * * * *) | telemetry.json, health_report, cost_report | optimization_pr, updated_manifest, cost_reduction_report | `optimize` |
| scale | optimize_complete \| manual | deployment_manifest, metrics, optimization_report | scaled_infrastructure, replication_manifests, cost_projection | `scale` |

## Composing Stages

Stages can be composed in three ways:

1. **Full pipeline** — run all 8 stages end-to-end via `pipeline.json`
2. **Partial pipeline** — start at any stage by setting `entry_point` in your manifest
3. **Single stage** — invoke an individual stage via its GitHub Actions job or webhook trigger

```json
// pipeline.json excerpt
{
  "entry_point": "build",
  "stages": ["build", "test", "deploy"]
}
```

## Invention Factory Use Case

The "Invention Factory" use case runs this pipeline fully autonomously:

1. A human submits a `problem_statement` to the **Discovery** stage
2. The AI designs, builds, tests, and deploys a solution
3. The system monitors itself and proposes improvements
4. The human only intervenes at governance gates (TAP protocol) for high-risk decisions

This enables a single human to oversee dozens of parallel invention streams.

## Related

- See [`pipeline.json`](./pipeline.json) for the master pipeline definition
- See [`.github/workflows/e2e-pipeline.yml`](../.github/workflows/e2e-pipeline.yml) for the GitHub Actions workflow
- See [`governance/`](../governance/) for TAP protocol and bounded-autonomy guardrails
