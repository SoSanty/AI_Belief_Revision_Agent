import unittest
from belief_base import BeliefBase, Atom, And, Or, Not, Implies
from contraction import partial_meet_contraction, entails

class TestContractionAGM(unittest.TestCase):

    def setUp(self):
        self.A = Atom("A")
        self.B = Atom("B")
        self.C = Atom("C")
        self.bb = BeliefBase()
        self.bb.expand(self.A)
        self.bb.expand(Implies(self.A, self.B))

    def test_closure(self):
        contracted = partial_meet_contraction(self.bb.beliefs, self.B, entails)
        for belief1 in contracted:
            for belief2 in contracted:
                if isinstance(belief1.formula, Implies):
                    antecedent = belief1.formula.antecedent
                    consequent = belief1.formula.consequent
                    antecedent_in = any(b.formula == antecedent for b in contracted)
                    consequent_in = any(b.formula == consequent for b in contracted)
                    if antecedent_in and not consequent_in:
                        self.fail(f"Closure violated: {antecedent} implies {consequent}, but {consequent} missing")

    def test_success(self):
        contracted = partial_meet_contraction(self.bb.beliefs, self.B, entails)
        for belief in contracted:
            self.assertNotEqual(belief.formula, self.B, "Success violated: ϕ still in B ÷ ϕ")

    def test_inclusion(self):
        original_set = set(self.bb.beliefs)
        contracted = set(partial_meet_contraction(self.bb.beliefs, self.B, entails))
        self.assertTrue(contracted.issubset(original_set), "Inclusion violated: B ÷ ϕ is not subset of B")

    def test_vacuity(self):
        D = Atom("D")  # D not related
        contracted = partial_meet_contraction(self.bb.beliefs, D, entails)
        original_set = set(self.bb.beliefs)
        contracted_set = set(contracted)
        self.assertEqual(original_set, contracted_set, "Vacuity violated: B ÷ ϕ ≠ B when ϕ ∉ Cn(B)")

    def test_extensionality(self):
        bb1 = BeliefBase()
        bb1.expand(self.A)
        bb1.expand(Implies(self.A, self.B))

        bb2 = BeliefBase()
        bb2.expand(self.A)
        bb2.expand(Implies(self.A, self.B))

        phi = self.B
        psi = Or(self.B, And(self.B, self.B))  # B logically equivalent to (B ∨ (B ∧ B))

        contracted_phi = set(partial_meet_contraction(bb1.beliefs, phi, entails))
        contracted_psi = set(partial_meet_contraction(bb2.beliefs, psi, entails))

        self.assertEqual(contracted_phi, contracted_psi, "Extensionality violated: B ÷ ϕ ≠ B ÷ ψ")

    def test_recovery(self):
        contracted = set(partial_meet_contraction(self.bb.beliefs, self.B, entails))
        recovered = contracted.copy()
        recovered.add(self.Belief(self.B))  # Expand back with ϕ
        original_set = set(self.bb.beliefs)
        for belief in original_set:
            self.assertIn(belief, recovered, "Recovery violated: could not recover original belief after adding ϕ")

    def test_conjunctive_inclusion(self):
        conjunct = And(self.A, self.B)
        contracted_conjunct = set(partial_meet_contraction(self.bb.beliefs, conjunct, entails))
        contracted_phi = set(partial_meet_contraction(self.bb.beliefs, self.A, entails))
        self.assertTrue(contracted_conjunct.issubset(contracted_phi), "Conjunctive Inclusion violated")

    def test_conjunctive_overlap(self):
        contracted_phi = set(partial_meet_contraction(self.bb.beliefs, self.A, entails))
        contracted_psi = set(partial_meet_contraction(self.bb.beliefs, self.B, entails))
        contracted_conjunct = set(partial_meet_contraction(self.bb.beliefs, And(self.A, self.B), entails))
        overlap = contracted_phi.intersection(contracted_psi)
        self.assertTrue(overlap.issubset(contracted_conjunct), "Conjunctive Overlap violated")

    class Belief:
        def __init__(self, formula, priority=0):
            self.formula = formula
            self.priority = priority

        def __eq__(self, other):
            return isinstance(other, TestContractionAGM.Belief) and self.formula == other.formula

        def __hash__(self):
            return hash(self.formula)

if __name__ == "__main__":
    unittest.main()
