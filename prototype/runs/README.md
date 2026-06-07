# Prototype Runs

This folder stores raw generated run artifacts when the prototype is executed.
The raw files are intentionally not tracked in Git because they are rebuildable
and relatively large.

Tracked evidence is kept in:

- `experiments/runs/`
- `results/tables/`
- `results/plots/`
- `results/FINDINGS.md`
- `reports/iteration/`

To regenerate runs, use:

```bash
make reproduce
```
