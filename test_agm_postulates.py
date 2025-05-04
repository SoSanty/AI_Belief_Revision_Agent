import unittest
from belief_base import BeliefBase, Atom, And, Not, Implies
from contraction import partial_meet_contraction
from entailment import check_entailment, logically_equivalent


class TestExpansionPostulates(unittest.TestCase):
    # Setup method to initialize a new belief base before each test
    def setUp(self):
        self.base = BeliefBase()

    # Test for the success postulate: φ should be added to the belief base after expansion
    def test_success_postulate(self):
        phi = Atom("A")
        self.base.expand(phi)  # Expanding belief base with phi
        formulas = [belief.formula for belief in self.base.beliefs]
        # Assert that phi is in the belief base after expansion
        self.assertTrue(any(str(belief) == str(phi) for belief in formulas),
                        "Success postulate failed: φ not found in belief base after expansion.")

    # Test for the inclusion postulate: The belief base should not shrink after expansion
    def test_inclusion_postulate(self):
        phi = Atom("A")
        initial_size = len(self.base.beliefs)
        self.base.expand(phi)  # Expanding belief base with phi
        # Assert that the belief base has grown or stayed the same
        self.assertGreaterEqual(len(self.base.beliefs), initial_size,
                                "Inclusion postulate failed: Belief base shrunk after expansion.")

    # Test for the vacuity postulate: Expanding with a formula independent of others should behave as simple addition
    def test_vacuity_postulate(self):
        phi = Atom("A")
        self.base.expand(phi)  # Expanding belief base with phi
        phi2 = Atom("B")
        self.base.expand(phi2)  # Expanding belief base with phi2
        formulas = [belief.formula for belief in self.base.beliefs]
        # Assert that phi2 is added independently to the belief base
        self.assertTrue(any(str(belief) == str(phi2) for belief in formulas),
                        "Vacuity postulate failed: Adding independent formula did not behave as simple addition.")

    # Test for the consistency after expansion: Belief base should become inconsistent if expanded with a contradiction
    def test_consistency_after_expansion(self):
        phi = And(Atom("A"), Not(Atom("A")))  # Contradiction: A and Not(A)
        self.base.expand(phi)  # Expanding belief base with a contradiction
        # Assert that the belief base is inconsistent after the expansion
        self.assertFalse(self.base.is_consistent(),
                         "Consistency postulate failed: Expanding with contradiction did not detect inconsistency.")


class TestContractionPostulates(unittest.TestCase):
    # Setup method to initialize a belief base with some beliefs before each test
    def setUp(self):
        self.base = BeliefBase()
        self.base.expand(Atom("A"))
        self.base.expand(Implies(Atom("A"), Atom("B")))  # Expanding with implications

    # Test for the success postulate during contraction: Should not entail phi after contraction
    def test_success_postulate_contraction(self):
        phi = Atom("B")
        contracted = partial_meet_contraction(self.base, phi)  # Performing contraction
        new_base = BeliefBase()
        for belief in contracted:
            new_base.expand(belief.formula, belief.priority)  # Expanding contracted beliefs into new base
        # Assert that phi is not entailed in the new belief base after contraction
        self.assertFalse(check_entailment(new_base, phi),
                         "Success postulate failed: After contraction, B should not be entailed.")

    # Test for the inclusion postulate during contraction: The beliefs in the contracted base should be a subset of the original
    def test_inclusion_postulate_contraction(self):
        phi = Atom("B")
        contracted = partial_meet_contraction(self.base, phi)
        # Assert that all beliefs in the contracted base were originally in the belief base
        self.assertTrue(all(b in self.base.beliefs for b in contracted),
                        "Inclusion postulate failed: Contraction produced beliefs outside original base.")

    # Test for the vacuity postulate during contraction: Contraction of a non-believed formula should not change the base
    def test_vacuity_postulate_contraction(self):
        phi = Atom("C")  # "C" is not believed initially
        contracted = partial_meet_contraction(self.base, phi)
        # Assert that the contracted base is the same as the original base
        self.assertEqual(set(contracted), set(self.base.beliefs),
                         "Vacuity postulate failed: Contraction of non-believed formula changed the base.")

    # Test for the consistency after contraction: The belief base should remain consistent after contraction
    def test_consistency_after_contraction(self):
        phi = Atom("B")
        contracted = partial_meet_contraction(self.base, phi)
        new_base = BeliefBase()
        for belief in contracted:
            new_base.expand(belief.formula, belief.priority)
        # Assert that the new belief base is consistent after contraction
        self.assertTrue(new_base.is_consistent(),
                        "Consistency postulate failed: Contracted base became inconsistent.")

    # Test for the extensionality postulate during contraction: Equivalent formulas should result in the same contracted base
    def test_extensionality_postulate(self):
        A = Atom("A")
        B = Atom("B")
        phi = And(A, B)
        psi = And(B, A)  # Equivalent formula to phi
        new_base = BeliefBase()
        new_base.expand(A)
        new_base.expand(B)  # Expanding belief base with A and B
        print("Beliefs before contraction:", [belief.formula for belief in new_base.beliefs])
        contracted_phi = partial_meet_contraction(new_base, phi)  # Contraction with phi
        contracted_psi = partial_meet_contraction(new_base, psi)  # Contraction with psi (equivalent to phi)
        print("Beliefs after contracting phi:", [belief.formula for belief in contracted_phi])
        print("Beliefs after contracting psi:", [belief.formula for belief in contracted_psi])
        # Assert that contracting phi and psi produces the same result
        self.assertEqual(set(contracted_phi), set(contracted_psi),
                         "Extensionality postulate failed: Contracting equivalent formulas gave different results.")


# Entry point for running the test cases
if __name__ == "__main__":
    unittest.main()
