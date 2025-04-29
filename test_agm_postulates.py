import unittest
from belief_base import BeliefBase, Atom, And, Not, Implies

class TestAGMPostulates(unittest.TestCase):

    def setUp(self):
        self.base = BeliefBase()

    def test_success_postulate(self):
        # Success: If expanding with φ, then φ must be in the belief base.
        phi = Atom("A")
        self.base.expand(phi)
        formulas = [belief.formula for belief in self.base.beliefs]
        self.assertTrue(any(str(belief) == str(phi) for belief in formulas), "Success postulate failed: φ not found in belief base after expansion.")

    def test_inclusion_postulate(self):
        # Inclusion: Expansion should only add, not remove existing beliefs.
        phi = Atom("A")
        initial_size = len(self.base.beliefs)
        self.base.expand(phi)
        self.assertGreaterEqual(len(self.base.beliefs), initial_size, "Inclusion postulate failed: Belief base shrunk after expansion.")

    def test_vacuity_postulate(self):
        # Vacuity: Expanding with a belief not conflicting with current base should behave like simple addition.
        phi = Atom("A")
        self.base.expand(phi)
        phi2 = Atom("B")
        self.base.expand(phi2)
        formulas = [belief.formula for belief in self.base.beliefs]
        self.assertTrue(any(str(belief) == str(phi2) for belief in formulas), "Vacuity postulate failed: Adding independent formula did not behave as simple addition.")

if __name__ == "__main__":
    unittest.main()