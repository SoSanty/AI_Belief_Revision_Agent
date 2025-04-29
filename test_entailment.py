import unittest
from partB import (
    eliminate_biconditional_obj,
    eliminate_implication_obj,
    move_negation_inward_obj,
    distribute_or_over_and_obj,
    extract_clauses_obj,
    to_cnf_obj,
    check_entailment,
)
from belief_base import Atom, And, Or, Not, Implies, Biconditional, BeliefBase


class TestPartB(unittest.TestCase):

    def test_eliminate_biconditional(self):
        A, B = Atom('A'), Atom('B')
        formula = Biconditional(A, B)
        result = eliminate_biconditional_obj(formula)
        self.assertIsInstance(result, And)
        self.assertTrue(all(isinstance(op, Implies) for op in result.operands))

    def test_eliminate_implication(self):
        A, B = Atom('A'), Atom('B')
        formula = Implies(A, B)
        result = eliminate_implication_obj(formula)
        self.assertIsInstance(result, Or)
        self.assertIsInstance(result.operands[0], Not)
        self.assertEqual(str(result.operands[0].operand), 'A')
        self.assertEqual(str(result.operands[1]), 'B')

    def test_move_negation(self):
        A, B = Atom('A'), Atom('B')
        formula = Not(And(A, B))  # ¬(A ∧ B)
        result = move_negation_inward_obj(formula)
        self.assertIsInstance(result, Or)
        self.assertTrue(all(isinstance(op, Not) for op in result.operands))

    def test_distribute_or_over_and(self):
        A, B, C = Atom('A'), Atom('B'), Atom('C')
        formula = Or(A, And(B, C))  # A ∨ (B ∧ C)
        result = distribute_or_over_and_obj(formula)
        self.assertIsInstance(result, And)
        self.assertTrue(all(isinstance(op, Or) for op in result.operands))

    def test_extract_clauses(self):
        A, B = Atom('A'), Atom('B')
        formula = And(Or(A, Not(B)), A)
        clauses = extract_clauses_obj(formula)
        self.assertEqual(len(clauses), 2)
        self.assertIn('A', clauses[1])
        self.assertIn('~B', clauses[0])

    def test_to_cnf(self):
        A, B = Atom('A'), Atom('B')
        formula = Implies(A, B)
        cnf = to_cnf_obj(formula)
        self.assertEqual(cnf, [{ '~A', 'B' }])

    def test_check_entailment_true(self):
        A, B = Atom('A'), Atom('B')
        base = BeliefBase()
        base.expand(Implies(A, B))
        base.expand(A)
        self.assertTrue(check_entailment(base, B))

    def test_check_entailment_false(self):
        A, B = Atom('A'), Atom('B')
        base = BeliefBase()
        base.expand(Implies(A, B))
        self.assertFalse(check_entailment(base, B))


if __name__ == '__main__':
    unittest.main()


