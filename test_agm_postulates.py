import unittest
from belief_base import BeliefBase, Atom, And, Not, Implies
from BeliefBaseContraction import partial_meet_contraction
from partB import logically_equivalent

class TestExpansionPostulates(unittest.TestCase):

    def setUp(self):
        self.base = BeliefBase()

    def test_success_postulate(self):
        phi = Atom("A")
        self.base.expand(phi)
        formulas = [belief.formula for belief in self.base.beliefs]
        self.assertTrue(any(str(belief) == str(phi) for belief in formulas), "Success postulate failed: φ not found in belief base after expansion.")

    def test_inclusion_postulate(self):
        phi = Atom("A")
        initial_size = len(self.base.beliefs)
        self.base.expand(phi)
        self.assertGreaterEqual(len(self.base.beliefs), initial_size, "Inclusion postulate failed: Belief base shrunk after expansion.")

    def test_vacuity_postulate(self):
        phi = Atom("A")
        self.base.expand(phi)
        phi2 = Atom("B")
        self.base.expand(phi2)
        formulas = [belief.formula for belief in self.base.beliefs]
        self.assertTrue(any(str(belief) == str(phi2) for belief in formulas), "Vacuity postulate failed: Adding independent formula did not behave as simple addition.")

    def test_consistency_after_expansion(self):
        phi = And(Atom("A"), Not(Atom("A")))
        self.base.expand(phi)
        self.assertFalse(self.base.is_consistent(), "Consistency postulate failed: Expanding with contradiction did not detect inconsistency.")

class TestContractionPostulates(unittest.TestCase):

    def setUp(self):
        self.base = BeliefBase()
        self.base.expand(Atom("A"))
        self.base.expand(Implies(Atom("A"), Atom("B")))

    def test_success_postulate_contraction(self):
        contracted = partial_meet_contraction(self.base, "B")
        new_base = BeliefBase()
        for belief in contracted:
            new_base.expand(belief.formula, belief.priority)
        from partB import check_entailment
        self.assertFalse(check_entailment(new_base, "B"), "Success postulate failed: After contraction, B should not be entailed.")

    def test_inclusion_postulate_contraction(self):
        contracted = partial_meet_contraction(self.base, "B")
        self.assertTrue(all(b in self.base.beliefs for b in contracted), "Inclusion postulate failed: Contraction produced beliefs outside original base.")

    def test_vacuity_postulate_contraction(self):
        contracted = partial_meet_contraction(self.base, "C")  # "C" not entailed initially
        self.assertEqual(set(contracted), set(self.base.beliefs), "Vacuity postulate failed: Contraction of non-believed formula changed the base.")

    def test_consistency_after_contraction(self):
        contracted = partial_meet_contraction(self.base, "B")
        new_base = BeliefBase()
        for belief in contracted:
            new_base.expand(belief.formula, belief.priority)
        self.assertTrue(new_base.is_consistent(), "Consistency postulate failed: Contracted base became inconsistent.")

    def test_extensionality_postulate(self):
        phi = And(Atom("A"), Atom("B"))
        psi = And(Atom("B"), Atom("A"))
        new_base = BeliefBase()
        new_base.expand(Atom("A"), priority=5)  # Manually set priority
        new_base.expand(Atom("B"), priority=5)  # Manually set priority
        contracted_phi = partial_meet_contraction(new_base, phi)
        contracted_psi = partial_meet_contraction(new_base, psi)
        self.assertEqual(contracted_phi, contracted_psi, "Extensionality postulate failed: Contracting equivalent formulas gave different results.")

if __name__ == "__main__":
    unittest.main()