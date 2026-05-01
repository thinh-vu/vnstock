# 🤖 AI Agent Instructions for vnstock

This document serves as the absolute source of truth for Antigravity and any other AI agents operating within the `vnstock` repository. It defines the strict architectural guidelines, coding standards, and step-by-step workflow that MUST be followed during any development task.

---

## 🎯 Phase 1: Pre-Development (Understand & Plan)
Before writing any code, the agent MUST follow these steps:
1. **Understand the Facade**: Review `vnstock.ui` (Unified UI layer). Recognize that all user interactions happen exclusively through this facade. 
2. **Identify the Target Layer**: Determine exactly where the new logic belongs based on the **Strict Layered Architecture**:
    - `vnstock.ui`: Modifying public interfaces, auto-documentation (`show_api`), or routing. Contains NO data extraction logic.
    - `vnstock.explorer`: Building web scraping and unstructured data extraction for specific providers (e.g., VCI, KBS).
    - `vnstock.connector`: Integrating pure REST API connections (e.g., FMP, Binance).
    - `vnstock.core`: Managing shared utilities, registries, constants, and type definitions. Do NOT place domain-specific logic here.
3. **Dependency Check**: Avoid introducing any new third-party dependencies unless strictly necessary and explicitly approved by the user.

---

## 🏗️ Phase 2: Architecture & Design Patterns (Implementation)
When building or refactoring, strictly adhere to these core patterns:

### 2.1. Unified UI Layer (Facade Pattern)
- `vnstock.ui` acts as a facade. Users interact ONLY with high-level domains (`Reference()`, `Market()`, `Fundamental()`).
- **Never** expose underlying data source complexity directly to the user.
- All UI methods MUST route logic through the `self._dispatch()` method using the `MAP` registry.

### 2.2. Provider Registry System (Registry / Factory Pattern)
- We strictly follow the **Open-Closed Principle**. To add a new data source, do NOT modify existing UI `if/else` logic.
- New data sources (explorers or connectors) must register themselves upon initialization using `vnstock.core.registry.ProviderRegistry`.
- *Example*: `ProviderRegistry.register('quote', 'kbs', KBSQuote)`

---

## 💻 Phase 3: Python Coding Conventions (Code Writing)
Write clean, maintainable, and highly optimized Python code:

- **Type Hinting & Circular Imports (`F821`)**: 
  - If a type hint requires an import that causes a circular dependency, do NOT place the `import` statement inside the function body. 
  - Instead, place it at the top of the file under a `from typing import TYPE_CHECKING` block.
- **Exception Handling (`E722`, `B904`)**: 
  - **No Bare Excepts**: NEVER use a bare `except:`. Always specify the exception type (e.g., `except Exception:` or `except ValueError:`).
  - **Exception Chaining**: When catching an exception to raise a new one, always use exception chaining (`raise CustomError(...) from e`) to preserve the traceback.
- **Variable Usage (`F841`)**: 
  - Never leave unused local variables in the code. Clean up any variables that are assigned but not read to optimize memory.

---

## 🚀 Phase 4: Unified Verification & Release Check (Quality & Tests)
Before finishing any task, committing changes, or releasing a new version, you MUST run the unified verification workflow.

This single command automatically:
1. **Auto-formats and Lints**: Uses `ruff` to fix style issues, unused imports, and conventions.
2. **Pre-commit Checks**: Runs all `pre-commit` hooks (trailing whitespace, EOF newlines).
3. **Automated Testing**: Executes the entire Pytest test suite (both Core and Unified UI) using the local codebase (`PYTHONPATH=.`).

**Run the unified workflow:**
```bash
make verify
```

*Note: If the `make verify` command fails at any step, the developer or agent MUST fix the reported issues and re-run the command until it passes successfully before committing.*
