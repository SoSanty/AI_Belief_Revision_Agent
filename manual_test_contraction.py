from contraction import partial_meet_contraction, entails
from belief_base import Atom, Implies, BeliefBase



def entails(belief_base, formula):
    """
    Check if belief_base logically entails formula.
    Replace with resolution/CNF method from your teammates.
    """
    # Example dummy logic: check if formula is in the base
    return formula in belief_base

# Costruzione della belief base
p = Atom("p")
q = Atom("q")
r = Atom("r")

p_implies_q = Implies(p, q)
q_implies_r = Implies(q, r)

beliefs = {p, p_implies_q, q_implies_r, r}
phi = r  # la formula da rimuovere

# Assegna le priorità (opzionale ma utile)
priorities = {
    p: 4,
    p_implies_q: 3,
    q_implies_r: 2,
    r: 1
}

# Esegui contraction
contracted = partial_meet_contraction(beliefs, phi, priorities, entails)

# Stampa i risultati
print("Original Beliefs:")
for b in beliefs:
    print("-", b)

print("\nFormula to contract (φ):", phi)

print("\nContracted Belief Base:")
for b in contracted:
    print("-", b)
