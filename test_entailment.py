import pytest
from belief_base import BeliefBase, Atom, And, Or, Not, Implies
from partB import to_cnf, entails

def check_entailment_from_belief_base(belief_base: BeliefBase, query: str) -> bool:
    kb_formulas = [str(belief) for belief in belief_base.beliefs]
    kb_clauses = []
    for formula in kb_formulas:
        kb_clauses.extend(to_cnf(formula))
    return entails(kb_clauses, query)


def test_super_complex_entailment():
    bb = BeliefBase()

    # Base molto complessa, logica articolata e interdipendente
    bb.expand(Implies(And(Atom("P"), Atom("Q")), Atom("R")))             # (P ∧ Q) → R
    bb.expand(Implies(Atom("R"), Or(Atom("S"), Atom("T"))))              # R → (S ∨ T)
    bb.expand(Implies(And(Atom("S"), Not(Atom("U"))), Atom("V")))        # (S ∧ ¬U) → V
    bb.expand(Implies(Atom("T"), Atom("U")))                             # T → U
    bb.expand(Implies(Atom("V"), Atom("W")))                             # V → W
    bb.expand(Atom("P"))
    bb.expand(Atom("Q"))

    # Con queste premesse, possiamo arrivare fino a W.
    # Catena: P ∧ Q → R → (S ∨ T)
    # Se S è vero e U è falso, V è vero → W
    # Ma se T è vero → U è vero → ¬U è falso → V è falso → W no
    # Se S è vero, U è falso → V vero → W vero ✅

    # Quindi: possiamo derivare W, solo se la disgiunzione R → (S ∨ T) va su S, e U è falsa implicitamente
    # Non possiamo dire W è garantito, a meno che non sia esplicitato che U è falsa
    # Ma nel nostro KB non si esclude U, quindi non possiamo garantire V né W
    # Ma possiamo garantire **R** e **S ∨ T** e **U** (da T)

    # Test di entailment su W (che non può essere garantito senza info su U)
    assert not check_entailment_from_belief_base(bb, "W")  # Non garantito

    # Test su R
    assert check_entailment_from_belief_base(bb, "R")

    # Test su S ∨ T (è implicato da R)
    assert check_entailment_from_belief_base(bb, "S | T")

    # Se aggiungiamo ¬U e S, allora possiamo derivare W!
    bb.expand(Atom("S"))
    bb.expand(Not(Atom("U")))

    assert check_entailment_from_belief_base(bb, "W")
