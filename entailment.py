from typing import List, Set, FrozenSet
from belief_base import Atom, And, Or, Not, Implies, BeliefBase, Belief
import itertools
from belief_base import Biconditional

# Function to eliminate biconditionals (↔) by converting them into conjunctions of implications
def eliminate_biconditional_obj(formula):
    if isinstance(formula, Atom):
        return formula
    elif isinstance(formula, Not):
        return Not(eliminate_biconditional_obj(formula.operand))
    elif isinstance(formula, And):
        return And(*[eliminate_biconditional_obj(op) for op in formula.operands])
    elif isinstance(formula, Or):
        return Or(*[eliminate_biconditional_obj(op) for op in formula.operands])
    elif isinstance(formula, Implies):
        return Implies(
            eliminate_biconditional_obj(formula.antecedent),
            eliminate_biconditional_obj(formula.consequent)
        )
    elif isinstance(formula, Biconditional):
        # Convert Biconditional A ↔ B into (A → B) ∧ (B → A)
        left = eliminate_biconditional_obj(formula.left)
        right = eliminate_biconditional_obj(formula.right)
        return And(Implies(left, right), Implies(right, left))
    else:
        raise TypeError(f"Unsupported formula type: {type(formula)}")

# Function to eliminate implications (→) by converting them into disjunctions (¬A ∨ B)
def eliminate_implication_obj(formula):
    if isinstance(formula, Atom):
        return formula
    elif isinstance(formula, Not):
        return Not(eliminate_implication_obj(formula.operand))
    elif isinstance(formula, And):
        return And(*[eliminate_implication_obj(op) for op in formula.operands])
    elif isinstance(formula, Or):
        return Or(*[eliminate_implication_obj(op) for op in formula.operands])
    elif isinstance(formula, Implies):
        antecedent = eliminate_implication_obj(formula.antecedent)
        consequent = eliminate_implication_obj(formula.consequent)
        # Convert implication into disjunction: A → B = ¬A ∨ B
        return Or(Not(antecedent), consequent)
    elif isinstance(formula, Biconditional):
        simplified = eliminate_biconditional_obj(formula)
        return eliminate_implication_obj(simplified)
    else:
        raise TypeError(f"Unsupported formula type: {type(formula)}")

# Function to move negations inward following De Morgan's laws and double negation elimination
def move_negation_inward_obj(formula):
    if isinstance(formula, Atom):
        return formula
    elif isinstance(formula, Not):
        inner = formula.operand
        if isinstance(inner, Atom):
            return formula
        elif isinstance(inner, Not):
            # Double negation: ¬(¬A) ⇒ A
            return move_negation_inward_obj(inner.operand)
        elif isinstance(inner, And):
            # De Morgan: ¬(A ∧ B) ⇒ ¬A ∨ ¬B
            return Or(*[move_negation_inward_obj(Not(op)) for op in inner.operands])
        elif isinstance(inner, Or):
            # De Morgan: ¬(A ∨ B) ⇒ ¬A ∧ ¬B
            return And(*[move_negation_inward_obj(Not(op)) for op in inner.operands])
        else:
            raise TypeError(f"Negation must be pushed after eliminating implications: {type(inner)}")
    elif isinstance(formula, And):
        return And(*[move_negation_inward_obj(op) for op in formula.operands])
    elif isinstance(formula, Or):
        return Or(*[move_negation_inward_obj(op) for op in formula.operands])
    else:
        raise TypeError(f"Unsupported formula type: {type(formula)}")

# Function to apply distributivity of OR over AND
def distribute_or_over_and_obj(formula):
    if isinstance(formula, Atom) or isinstance(formula, Not):
        return formula
    elif isinstance(formula, And):
        return And(*[distribute_or_over_and_obj(op) for op in formula.operands])
    elif isinstance(formula, Or):
        # Apply distributive property of OR over AND
        left = distribute_or_over_and_obj(formula.operands[0])
        right = distribute_or_over_and_obj(formula.operands[1])
        
        if isinstance(left, And):
            # Apply distributivity: (A ∧ B) ∨ C = (A ∨ C) ∧ (B ∨ C)
            return And(*[
                distribute_or_over_and_obj(Or(op, right))
                for op in left.operands
            ])
        elif isinstance(right, And):
            # Apply distributivity: A ∨ (B ∧ C) = (A ∨ B) ∧ (A ∨ C)
            return And(*[
                distribute_or_over_and_obj(Or(left, op))
                for op in right.operands
            ])
        else:
            return Or(left, right)
    else:
        raise TypeError(f"Unsupported formula type: {type(formula)}")

# Function to extract literals (atoms or negated atoms) from a formula
def extract_literals_obj(formula) -> Set[str]:
    if isinstance(formula, Atom):
        return {formula.name}
    elif isinstance(formula, Not) and isinstance(formula.operand, Atom):
        # If it's a negation of an atom, return it as a negated literal
        return {f"~{formula.operand.name}"}
    elif isinstance(formula, Or):
        literals = set()
        for operand in formula.operands:
            literals.update(extract_literals_obj(operand))
        return literals
    else:
        raise TypeError(f"Expected a disjunction or literal in CNF, got {type(formula)}")

# Function to extract clauses (sets of literals) from a formula in conjunctive normal form (CNF)
def extract_clauses_obj(formula) -> List[Set[str]]:
    if isinstance(formula, And):
        clauses = []
        for operand in formula.operands:
            clauses.extend(extract_clauses_obj(operand))
        return clauses
    elif isinstance(formula, Or) or isinstance(formula, Atom) or (isinstance(formula, Not) and isinstance(formula.operand, Atom)):
        return [extract_literals_obj(formula)]
    else:
        raise TypeError(f"Expected CNF structure (And/Or/Atom/Not), got {type(formula)}")

# Function to convert a formula to conjunctive normal form (CNF)
def to_cnf_obj(formula) -> List[Set[str]]:
    # Step 1: Eliminate biconditionals (↔)
    step1 = eliminate_biconditional_obj(formula)
    # Step 2: Eliminate implications (→)
    step2 = eliminate_implication_obj(step1)
    # Step 3: Move negations inward
    step3 = move_negation_inward_obj(step2)
    # Step 4: Distribute OR over AND
    step4 = distribute_or_over_and_obj(step3)
    # Step 5: Extract clauses (sets of literals)
    return extract_clauses_obj(step4)

# Function to check entailment of a formula from a belief base using resolution
def check_entailment(belief_base: BeliefBase, query) -> bool:
    # Extract CNF clauses from each formula in the belief base
    kb_clauses = []
    for belief in belief_base.beliefs:
        kb_clauses.extend(to_cnf_obj(belief.formula))

    # Add query negation, transformed into CNF
    negated_query = Not(query)
    query_clauses = to_cnf_obj(negated_query)

    # Combine clauses from belief base and negated query
    clause_set = {frozenset(clause) for clause in kb_clauses + query_clauses}

    # Perform resolution to check if the clause set is unsatisfiable
    return resolution(clause_set)

# Function to perform the resolution procedure on a set of clauses
def resolution(clauses: Set[FrozenSet[str]]) -> bool:
    new = set()

    while True:
        # Generate all pairs of clauses
        pairs = [(c1, c2) for c1 in clauses for c2 in clauses if c1 != c2]

        for (c1, c2) in pairs:
            resolvents = resolve(set(c1), set(c2))
            if frozenset() in resolvents:
                return True
            new.update(resolvents)

        if new.issubset(clauses):
            return False

        clauses.update(new)

# Helper function to negate a literal (e.g., "~A" becomes "A" and vice versa)
def negate(literal: str) -> str:
    return literal[1:] if literal.startswith('~') else f"~{literal}"

# Function to resolve two clauses and return their resolvents
def resolve(clause1: Set[str], clause2: Set[str]) -> Set[FrozenSet[str]]:
    resolvents = set()

    for l1 in clause1:
        for l2 in clause2:
            if l1 == negate(l2):
                # Resolving literals that are negations of each other
                new_clause = (clause1 | clause2) - {l1, l2}
                # Ensure no contradiction occurs (no literal and its negation in the new clause)
                if not any(lit in new_clause and negate(lit) in new_clause for lit in new_clause):
                    resolvents.add(frozenset(new_clause))

    return resolvents

# Function to check if two formulas are logically equivalent in the context of a belief base
def logically_equivalent(belief_base: BeliefBase, phi, psi) -> bool:
    """
    Check if two formulas φ and ψ are logically equivalent in the context of a belief base.
    They are equivalent if φ entails ψ and ψ entails φ.
    """
    return (
        check_entailment(belief_base, Implies(phi, psi)) and
        check_entailment(belief_base, Implies(psi, phi))
    )
