# CI Recovery — jobs failing before checkout

Observed: 2026-09-22

## Evidence

The `JOSELYN CI` workflow is being parsed and runs are created, but GitHub-hosted jobs are terminating before any workflow step starts.

Current evidence:

- Run `#19` on `main` (`35776290063`) was created for commit `11b8cf23`.
- Python 3.11 and 3.12 jobs concluded `failure`.
- Python 3.13 concluded `cancelled`.
- The Jobs API reports `steps: null` for those jobs.
- The same pre-step failure pattern existed on earlier feature-branch and pull-request runs, including run `#16`.
- `.github/workflows/ci.yml` contains normal `checkout`, `setup-python`, install, unit-test and CLI smoke-test steps.

## Interpretation

This is a runner/account/policy startup failure until proven otherwise. A red Actions badge in this state is **not evidence that JOSELYN unit tests failed**, because no test step was started.

Do not change application code merely to make this badge green.

## Recovery checklist

1. Repository **Settings → Actions → General**
   - Confirm Actions are enabled.
   - Confirm GitHub-hosted actions are permitted by repository/account policy.
2. Account **Billing / Actions usage**
   - Confirm the account is permitted to start GitHub-hosted runners and has no billing/spending/account hold.
3. GitHub service health
   - Check for a hosted-runner incident if jobs still fail before `Checkout`.
4. Re-run the failed workflow.
5. Confirm the Jobs API/UI now shows real steps:
   - Checkout
   - Set up Python
   - Install package
   - Run tests
   - Smoke test CLI
6. Only after steps execute should a failure be treated as a code/test failure.

## Independent local gate

Until hosted runners start correctly, use:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v

joselyn status --format json
joselyn version --format json
joselyn event demo --type employee.created --format json
```

People Core v2 also requires explicit actor/role context, for example:

```bash
joselyn people list \
  --db joselyn.db \
  --actor HR-1 \
  --role "HR Manager" \
  --format json
```

## Exit condition

CI is considered recovered only when a fresh run reaches actual steps and the test/smoke commands complete successfully. `steps: null` is still infrastructure-blocked.
