# GitHub Templates

Reusable GitHub repository configuration templates for generated systems.

## Files

### `PULL_REQUEST_TEMPLATE.md`
Copy to `.github/PULL_REQUEST_TEMPLATE.md` in your generated repo. Enforces the Infinity Protocol checklist (TAP compliance, 110% Protocol, no secrets) on every PR.

### `ISSUE_TEMPLATE/`
Copy the entire directory to `.github/ISSUE_TEMPLATE/` in your generated repo.

| File | Use When |
|---|---|
| `bug_report.md` | Something is broken in a template or generated system |
| `feature_request.md` | Requesting a new template or capability |
| `new_template.md` | Proposing a new production-grade template to the library |
| `guardian_alert.md` | Auto-filed by the Guardian CI workflow; do not use manually |

### `workflows/`
Copy individual workflow files to `.github/workflows/` in your generated repo.

| File | Use When |
|---|---|
| `standard-ci.yml` | Any Python-based generated system; runs tests, lint (ruff), and CodeQL |
| `deploy-pages.yml` | Generated systems with a Next.js front-end deployed to GitHub Pages |

## Usage

```bash
# Bootstrap a new generated repo with all GitHub templates
cp -r templates/github/. <your-repo>/.github/
```
