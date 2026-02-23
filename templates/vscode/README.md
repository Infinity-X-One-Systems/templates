# VS Code Templates

Configuration and snippets for developing with the Infinity Template Library in VS Code.

## Files

### `infinity.code-workspace`
Open this workspace file (`File > Open Workspace from File`) to get a pre-configured VS Code environment with:
- **Python**: Ruff formatter, pytest test runner pointed at `.venv`
- **TypeScript**: Prettier formatter, ESLint
- **Launch configs**: FastAPI (port 8000) and Next.js Control Panel (port 3001)
- **Tasks**: Run all Python tests across the repo; compose a system from a manifest
- **File exclusions**: `__pycache__`, `.pytest_cache`, `node_modules`, `.next`
- **Extension recommendations**: Ruff, Prettier, Pylance, Copilot, Docker, Tailwind, ESLint

### `snippets/infinity-python.code-snippets`
Copy to `.vscode/infinity-python.code-snippets` in your project (or install globally via VS Code).

| Prefix | Generates |
|---|---|
| `inf-agent` | Infinity `AgentBase` subclass skeleton |
| `inf-model` | Pydantic `BaseModel` with `id` and `created_at` |
| `inf-engine` | Engine class with an in-memory store |
| `inf-test` | pytest test function |

### `snippets/infinity-typescript.code-snippets`
Copy to `.vscode/infinity-typescript.code-snippets` in your project.

| Prefix | Generates |
|---|---|
| `inf-api-route` | Next.js App Router API route (GET + POST, edge runtime) |
| `inf-component` | React client component with Tailwind classes |

## Quick Setup

```bash
# Open the workspace
code templates/vscode/infinity.code-workspace

# Or copy snippets into your project
cp templates/vscode/snippets/*.code-snippets <your-repo>/.vscode/
```
