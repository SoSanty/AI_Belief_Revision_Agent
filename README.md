# Belief Revision Agent — Interactive and Automated Testing

This belief revision system implements the AGM framework for propositional logic. It supports expansion, contraction, and revision, and checks for rationality using both symbolic CNF-based entailment and a model-based consistency checker.

---

## How to Test the Agent

You can test the system in two different ways:

### 1.Interactive Mode (Command Line)
Run the agent in an interactive loop:

```bash
python3 main.py
```

You'll be prompted with a menu:

```
1. View belief base
2. Expand belief base
3. Contract belief base
4. Exit
```

You can input complex formulas like:

```
(NOT B) AND (B OR C) OR (A AND (NOT C)) AND D
```
Make sure the parenthesis are correct in your input, otherwise there could be errors when expanding.

Biimplication (`<->`) and implication (`->`) are also supported.

### Example Scenario to Test All AGM Postulates

This sequence of inputs can be used to manually verify all expansion and contraction postulates:

#### Expansion Postulates:
- **Success**: Expand with `A` → `A` appears.
- **Inclusion**: Expand with `B` → `A, B` appear.
- **Vacuity**: Expand with `C` → no conflict.
- **Consistency**: Expand with `NOT A` → inconsistency is flagged.

#### Contraction Postulates:
- **Success**: Expand with `A`, `A -> B`, then contract `B` → `B` no longer entailed.
- **Inclusion**: Contracted base should only remove minimal elements.
- **Vacuity**: Contract `Z` (not entailed) → no change.
- **Consistency**: Expand `A`, `NOT A`, then contract `A` → base becomes consistent.
- **Extensionality**: Expand `A`, `B`, `(A AND B)`, then contract `(A AND B)` and `(B AND A)` → both give the same result.

---

### 2.Unit Test Mode

For a non-interactive, automated test of all AGM postulates and core logic, run:

```bash
python3 test_agm_postulates.py
```

This runs a suite of tests that validate:
- Symbolic parsing
- CNF conversion and resolution
- Expansion and contraction logic
- Satisfaction of all AGM postulates

---

## Notes

- The belief base uses symbolic formula objects (e.g., `Atom`, `And`, `Not`) to ensure clean logical manipulation.
- The CNF conversion and resolution engine is custom built and purely symbolic.
- Priorities are automatically assigned based on seniority and formula simplicity, and they influence contraction behavior.
