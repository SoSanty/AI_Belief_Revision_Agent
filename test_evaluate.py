import unittest
from belief_base import BeliefBase, Atom, And, Or, Not, Implies

class TestBeliefBase(unittest.TestCase):

    def setUp(self):
        self.A = Atom("A")
        self.B = Atom("B")
        self.C = Atom("C")
        self.bb = BeliefBase()
        # self.bb.expand(And(Atom("A"), Atom("B")))
        # self.bb.expand(Implies(Atom("A"), Not(Atom("B"))))
        # self.bb.expand(Implies(Atom("A"), Not(Atom("B"))))
        # self.bb.expand(Or(And(Atom("A"), Atom("B")), Not(Atom("A"))))
        # self.bb.expand(Implies(Atom("B"), Atom("A")))
        # self.bb.expand(Not(And(Atom("A"), Atom("B"))))

    def test_is_consistent(self):
        # First, add consistent beliefs
        self.bb.expand(And(Atom("A"), Atom("B")))
        self.assertTrue(self.bb.is_consistent(), "Expected belief base to be consistent after first belief.")
        print(f"Belief base after adding first belief: {self.bb}")

        # Then, add a belief that is consistent with the previous one
        self.bb.expand(Implies(Atom("A"), Not(Atom("C"))))
        self.assertTrue(self.bb.is_consistent(), "Expected belief base to be consistent after second belief.")
        print(f"Belief base after adding second belief: {self.bb}")

        # Then, add a belief that contradicts the previous one
        self.bb.expand(Implies(Atom("A"), Not(Atom("B"))))
        self.assertFalse(self.bb.is_consistent(), "Expected belief base to be inconsistent after contradictory belief.")
        print(f"Belief base after adding contradictory belief: {self.bb}")

    def test_expand(self):
        self.assertEqual(str(self.bb), "((A ∧ B) ∧ (A → ¬B) ∧ ((A ∧ B) ∨ ¬A) ∧ (B → A) ∧ ¬(A ∧ B))", f"Test failed: {self.bb}")
        self.assertEqual(self.bb.get_atoms(), {"A", "B"}, f"Test failed: {self.bb.get_atoms()}")
        self.assertEqual(self.bb.is_consistent(), True, f"Test failed: {self.bb.is_consistent()}")

    def test_get_atoms(self):
        self.bb.expand(And(self.A, self.B))
        self.bb.expand(Implies(self.A, Not(self.C)))
        self.bb.expand(Implies(self.A, Not(self.B)))
        self.assertEqual(self.bb.get_atoms(), {"A", "B", "C"}, f"Test failed: {self.bb.get_atoms()}")

    def test_formula_evaluation(self):
        model_true_false = {"A": True, "B": False}
        model_false_true = {"A": False, "B": True}
        model_all_true = {"A": True, "B": True}
        model_all_false = {"A": False, "B": False}

        tests = [
            (And(self.A, self.B), model_all_true, True),
            (And(self.A, self.B), model_true_false, False),
            (Or(self.A, self.B), model_true_false, True),
            (Or(self.A, self.B), model_all_false, False),
            (Not(self.A), model_true_false, False),
            (Not(self.B), model_true_false, True),
            (Implies(self.A, self.B), model_all_true, True),
            (Implies(self.A, self.B), model_true_false, False),
            (Implies(self.B, self.A), model_true_false, True),
        ]

        for i, (formula, model, expected) in enumerate(tests):
            with self.subTest(i=i):
                result = formula.evaluate(model)
                self.assertEqual(result, expected, f"Test {i+1} failed: {formula} with {model} → {result}, expected {expected}")

    def test_evaluate_all(self):
        model_true_false = {"A": True, "B": False}
        model_false_true = {"A": False, "B": True}
        model_all_true = {"A": True, "B": True}
        model_all_false = {"A": False, "B": False}

        self.assertFalse(self.bb.evaluate_all(model_all_true), f"Test failed: {self.bb} with {model_all_true}")
        self.assertFalse(self.bb.evaluate_all(model_true_false), f"Test failed: {self.bb} with {model_true_false}")
        self.assertFalse(self.bb.evaluate_all(model_all_false), f"Test failed: {self.bb} with {model_all_false}")
        self.assertFalse(self.bb.evaluate_all(model_false_true), f"Test failed: {self.bb} with {model_false_true}")

    def test_evaluate_any(self):
        model_true_false = {"A": True, "B": False}
        model_false_true = {"A": False, "B": True}
        model_all_true = {"A": True, "B": True}
        model_all_false = {"A": False, "B": False}

        self.assertTrue(self.bb.evaluate_any(model_all_true), f"Test failed: {self.bb} with {model_all_true}")
        self.assertTrue(self.bb.evaluate_any(model_true_false), f"Test failed: {self.bb} with {model_true_false}")
        self.assertTrue(self.bb.evaluate_any(model_all_false), f"Test failed: {self.bb} with {model_all_false}")
        self.assertTrue(self.bb.evaluate_any(model_false_true), f"Test failed: {self.bb} with {model_false_true}")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestBeliefBase('test_is_consistent'))
    suite.addTest(TestBeliefBase('test_get_atoms'))
    runner = unittest.TextTestRunner()
    runner.run(suite)
