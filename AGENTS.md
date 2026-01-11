## 1. Operational Rules

- **Execute Plan Completely**: Once a plan is set, execute the entire plan and stop asking for review until the whole plan is done. Do not pause for intermediate user confirmations unless critically stuck.
- publish commits to the branch every hour if you haven't finished
- give update every hour if not finished
- make sure .gitignore doesn't sync temporary files that are generated with running the code
  
## 2. Design Philosophy

-   **KISS:** Prioritize code that a junior developer can understand at a glance.
-   **DRY vs. AHA:** Avoid duplicating business logic, but do not abstract UI components until they are used in 3+ locations.
-   **SOLID (SRP):** Every file must have one clear purpose. If a function handles both 'fetching' and 'formatting', split it.
-   **YAGNI:** Never add new libraries or 'future-proof' features without explicit instruction.

## 3. Strict Development Guidelines
- **No Hand-holding:** Proceed with implementation once the plan is approved. Do not ask for permission on minor implementation details.
- **Code Style:** Prefer functional components over classes. Use early returns to reduce nesting.
- **Standard:** Use linting. Never bypass linting errors.
- **Dependency Management:** Never add new heavy dependencies without explicit reasoning in the plan.

## 4. Testing & Quality Gates
- **Requirement:** Every new feature MUST include a corresponding test file in the test folder.
- **Framework:** Use parameterized tests where possible.
- **Verification:** Always run test and linting before finalizing any task.

## 5. Explicit Boundaries (Do NOT Touch)
- **Forbidden:** Never modify files in `.github/workflows/` or `scripts/deploy.sh`.
- **Secrets:** Do not touch `.env.example` or any `.env` file.
- **Legacy:** Do not refactor `src/legacy/` unless specifically tasked.
