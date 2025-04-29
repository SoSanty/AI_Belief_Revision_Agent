import unittest
from belief_base import BeliefBase, Atom, And, Or, Not, Implies
from contraction import partial_meet_contraction, entails

class TestRevisionAGM(unittest.TestCase):

    def setUp(self):
        self.A = Atom("A")
        self.B = Atom("B")
        self.C = Atom("C")
        self.bb = BeliefBase()
        self.bb.expand(self.A)
        self.bb.expand(Implies(self.A, self.B))

    def revise(self, belief_base, formula):
        # Levi identity: (B ÷ ¬ϕ) + ϕ
        contracted = partial_meet_contraction(belief_base.beliefs, Not(formula), entails)
        belief_base.beliefs = list(contracted)
        belief_base.expand(formula)
        return belief_base

    def test_closure(self):
        revised = self.revise(self.bb, self.B)
        for belief1 in revised.beliefs:
            for belief2 in revised.beliefs:
                if isinstance(belief1.formula, Implies):
                    antecedent = belief1.formula.antecedent
                    consequent = belief1.formula.consequent
                    antecedent_in = any(b.formula == antecedent for b in revised.beliefs)
                    consequent_in = any(b.formula == consequent for b in revised.beliefs)
                    if antecedent_in and not consequent_in:
                        self.fail(f"Closure violated in revision: {antecedent} implies {consequent}, but {consequent} missing")

    def test_success(self):
        revised = self.revise(self.bb, self.B)
        self.assertTrue(any(belief.formula == self.B for belief in revised.beliefs), "Success violated: ϕ not in B ∗ ϕ")

    def test_inclusion(self):
        original_set = set(self.bb.beliefs)
        revised = self.revise(self.bb, self.B)
        new_set = set(revised.beliefs)
        for belief in new_set:
            self.assertIn(belief, original_set.union({self.B}), "Inclusion violated: B ∗ ϕ not subset of B + ϕ")

    def test_vacuity(self):
        D = Atom("D")
        revised = self.revise(self.bb, D)
        bb_plus_D = BeliefBase()
        bb_plus_D.beliefs = list(self.bb.beliefs)
        bb_plus_D.expand(D)
        self.assertEqual(set(revised.beliefs), set(bb_plus_D.beliefs), "Vacuity violated: B ∗ ϕ ≠ B + ϕ when ¬ϕ ∉ B")

    def test_consistency(self):
        revised = self.revise(self.bb, self.B)
        self.assertTrue(revised.is_consistent(), "Consistency violated: B ∗ ϕ is inconsistent")

    def test_extensionality(self):
        bb1 = BeliefBase()
        bb1.expand(self.A)
        bb1.expand(Implies(self.A, self.B))

        bb2 = BeliefBase()
        bb2.expand(self.A)
        bb2.expand(Implies(self.A, self.B))

        phi = self.B
        psi = Or(self.B, And(self.B, self.B))  # B ↔ (B ∨ (B ∧ B))

        revised_phi = self.revise(bb1, phi)
        revised_psi = self.revise(bb2, psi)

        self.assertEqual(set(revised_phi.beliefs), set(revised_psi.beliefs), "Extensionality violated: B ∗ ϕ ≠ B ∗ ψ")

    def test_superexpansion(self):
        conjunct = And(self.A, self.B)
        revised_conjunct = self.revise(self.bb, conjunct)

        revised_phi = self.revise(self.bb, self.A)
        revised_phi.expand(self.B)

        self.assertTrue(set(revised_conjunct.beliefs).issubset(set(revised_phi.beliefs)),
                        "Superexpansion violated: B ∗ (ϕ ∧ ψ) ⊄ (B ∗ ϕ) + ψ")

    def test_subexpansion(self):
        revised_phi = self.revise(self.bb, self.A)
        if not any(belief.formula == Not(self.B) for belief in revised_phi.beliefs):
            revised_phi_plus_psi = BeliefBase()
            revised_phi_plus_psi.beliefs = list(revised_phi.beliefs)
            revised_phi_plus_psi.expand(self.B)

            revised_conjunct = self.revise(self.bb, And(self.A, self.B))
            self.assertTrue(set(revised_phi_plus_psi.beliefs).issubset(set(revised_conjunct.beliefs)),
                            "Subexpansion violated: (B ∗ ϕ) + ψ ⊄ B ∗ (ϕ ∧ ψ)")

if __name__ == "__main__":
    unittest.main()
