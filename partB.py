# B_entailment.py
from typing import List, Set, FrozenSet
from belief_base import BeliefBase
import re


def negate(literal: str) -> str:
    """
    Negate a literal.
    Example: negate("A") -> "~A", negate("~A") -> "A"
    """
    if literal.startswith('~'):
        return literal[1:]
    else:
        return f"~{literal}"


def tokenize(formula: str) -> List[str]:
    """
    Tokenize a formula string into a list of tokens using logical operator names.
    Supported operators: and, or, not, implies, iff
    """
    # Replace logical names with equivalent short symbols for internal parsing
    formula = (formula.replace(' and ', ' & ')
                     .replace(' or ', ' | ')
                     .replace(' implies ', ' > ')
                     .replace(' iff ', ' = ')
                     .replace(' not ', ' ~ '))
    
    # Ensure spaces around operators and parentheses
    formula = (formula.replace('&', ' & ').replace('|', ' | ')
                     .replace('>', ' > ').replace('=', ' = ')
                     .replace('(', ' ( ').replace(')', ' ) '))
    
    # Split by spaces and filter out empty strings
    return [token for token in formula.split() if token]


def parse_formula(tokens: List[str]) -> dict:
    """
    Parse a formula from tokens using recursive descent parsing.
    Returns a tree representation of the formula.
    """
    def parse_biconditional():
        left = parse_implication()
        while tokens and tokens[0] == '=':
            tokens.pop(0)  # Remove '='
            right = parse_implication()
            left = {'type': 'biconditional', 'left': left, 'right': right}
        return left
    
    def parse_implication():
        left = parse_disjunction()
        while tokens and tokens[0] == '>':
            tokens.pop(0)  # Remove '>'
            right = parse_disjunction()
            left = {'type': 'implication', 'left': left, 'right': right}
        return left
    
    def parse_disjunction():
        left = parse_conjunction()
        while tokens and tokens[0] == '|':
            tokens.pop(0)  # Remove '|'
            right = parse_conjunction()
            left = {'type': 'disjunction', 'left': left, 'right': right}
        return left
    
    def parse_conjunction():
        left = parse_negation()
        while tokens and tokens[0] == '&':
            tokens.pop(0)  # Remove '&'
            right = parse_negation()
            left = {'type': 'conjunction', 'left': left, 'right': right}
        return left
    
    def parse_negation():
        if tokens and tokens[0] == '~':
            tokens.pop(0)  # Remove '~'
            expr = parse_negation()
            return {'type': 'negation', 'expression': expr}
        return parse_atom()
    
    def parse_atom():
        if tokens and tokens[0] == '(':
            tokens.pop(0)  # Remove '('
            expr = parse_biconditional()
            if tokens and tokens[0] == ')':
                tokens.pop(0)  # Remove ')'
            return expr
        elif tokens:
            atom = tokens.pop(0)
            return {'type': 'literal', 'value': atom}
        else:
            raise ValueError("Unexpected end of formula")
    
    # Make a copy of the tokens to avoid modifying the original
    tokens_copy = tokens.copy()
    return parse_biconditional()


def eliminate_biconditional(formula: dict) -> dict:
    """
    Eliminate biconditional (↔) operators from a formula.
    A ↔ B becomes (A → B) ∧ (B → A)
    """
    if formula['type'] == 'literal':
        return formula
    elif formula['type'] == 'negation':
        return {
            'type': 'negation',
            'expression': eliminate_biconditional(formula['expression'])
        }
    elif formula['type'] == 'conjunction' or formula['type'] == 'disjunction':
        return {
            'type': formula['type'],
            'left': eliminate_biconditional(formula['left']),
            'right': eliminate_biconditional(formula['right'])
        }
    elif formula['type'] == 'implication':
        return {
            'type': 'implication',
            'left': eliminate_biconditional(formula['left']),
            'right': eliminate_biconditional(formula['right'])
        }
    elif formula['type'] == 'biconditional':
        left = eliminate_biconditional(formula['left'])
        right = eliminate_biconditional(formula['right'])
        
        # (A ↔ B) becomes (A → B) ∧ (B → A)
        implication1 = {
            'type': 'implication',
            'left': left,
            'right': right
        }
        
        implication2 = {
            'type': 'implication',
            'left': right,
            'right': left
        }
        
        return {
            'type': 'conjunction',
            'left': implication1,
            'right': implication2
        }


def eliminate_implication(formula: dict) -> dict:
    """
    Eliminate implication (→) operators from a formula.
    A → B becomes ¬A ∨ B
    """
    if formula['type'] == 'literal':
        return formula
    elif formula['type'] == 'negation':
        return {
            'type': 'negation',
            'expression': eliminate_implication(formula['expression'])
        }
    elif formula['type'] == 'conjunction' or formula['type'] == 'disjunction':
        return {
            'type': formula['type'],
            'left': eliminate_implication(formula['left']),
            'right': eliminate_implication(formula['right'])
        }
    elif formula['type'] == 'implication':
        left = eliminate_implication(formula['left'])
        right = eliminate_implication(formula['right'])
        
        # A → B becomes ¬A ∨ B
        return {
            'type': 'disjunction',
            'left': {
                'type': 'negation',
                'expression': left
            },
            'right': right
        }


def move_negation_inward(formula: dict) -> dict:
    """
    Move negation inward using De Morgan's laws.
    ¬(A ∧ B) becomes ¬A ∨ ¬B
    ¬(A ∨ B) becomes ¬A ∧ ¬B
    ¬¬A becomes A
    """
    if formula['type'] == 'literal':
        return formula
    elif formula['type'] == 'negation':
        if formula['expression']['type'] == 'negation':
            # Double negation: ¬¬A becomes A
            return move_negation_inward(formula['expression']['expression'])
        elif formula['expression']['type'] == 'conjunction':
            # De Morgan: ¬(A ∧ B) becomes ¬A ∨ ¬B
            return {
                'type': 'disjunction',
                'left': move_negation_inward({
                    'type': 'negation',
                    'expression': formula['expression']['left']
                }),
                'right': move_negation_inward({
                    'type': 'negation',
                    'expression': formula['expression']['right']
                })
            }
        elif formula['expression']['type'] == 'disjunction':
            # De Morgan: ¬(A ∨ B) becomes ¬A ∧ ¬B
            return {
                'type': 'conjunction',
                'left': move_negation_inward({
                    'type': 'negation',
                    'expression': formula['expression']['left']
                }),
                'right': move_negation_inward({
                    'type': 'negation',
                    'expression': formula['expression']['right']
                })
            }
        elif formula['expression']['type'] == 'literal':
            # Keep the negation for literals
            return formula
    elif formula['type'] == 'conjunction' or formula['type'] == 'disjunction':
        return {
            'type': formula['type'],
            'left': move_negation_inward(formula['left']),
            'right': move_negation_inward(formula['right'])
        }
    
    return formula


def distribute_or_over_and(formula: dict) -> dict:
    """
    Distribute OR over AND: A ∨ (B ∧ C) becomes (A ∨ B) ∧ (A ∨ C)
    """
    if formula['type'] == 'literal' or formula['type'] == 'negation':
        return formula
    elif formula['type'] == 'conjunction':
        return {
            'type': 'conjunction',
            'left': distribute_or_over_and(formula['left']),
            'right': distribute_or_over_and(formula['right'])
        }
    elif formula['type'] == 'disjunction':
        left = distribute_or_over_and(formula['left'])
        right = distribute_or_over_and(formula['right'])
        
        # If right is a conjunction, distribute left over it
        if right['type'] == 'conjunction':
            return {
                'type': 'conjunction',
                'left': distribute_or_over_and({
                    'type': 'disjunction',
                    'left': left,
                    'right': right['left']
                }),
                'right': distribute_or_over_and({
                    'type': 'disjunction',
                    'left': left,
                    'right': right['right']
                })
            }
        # If left is a conjunction, distribute right over it
        elif left['type'] == 'conjunction':
            return {
                'type': 'conjunction',
                'left': distribute_or_over_and({
                    'type': 'disjunction',
                    'left': left['left'],
                    'right': right
                }),
                'right': distribute_or_over_and({
                    'type': 'disjunction',
                    'left': left['right'],
                    'right': right
                })
            }
        # If neither is a conjunction, return as is
        else:
            return {
                'type': 'disjunction',
                'left': left,
                'right': right
            }


def extract_literals(formula: dict) -> Set[str]:
    """
    Extract literals from a formula in CNF.
    """
    if formula['type'] == 'literal':
        return {formula['value']}
    elif formula['type'] == 'negation' and formula['expression']['type'] == 'literal':
        return {f"~{formula['expression']['value']}"}
    elif formula['type'] == 'disjunction':
        return extract_literals(formula['left']).union(extract_literals(formula['right']))
    return set()


def extract_clauses(formula: dict) -> List[Set[str]]:
    """
    Extract clauses from a formula in CNF.
    """
    if formula['type'] == 'conjunction':
        return extract_clauses(formula['left']) + extract_clauses(formula['right'])
    elif formula['type'] == 'disjunction' or formula['type'] == 'literal' or formula['type'] == 'negation':
        return [extract_literals(formula)]
    return []


def to_cnf(formula: str) -> List[Set[str]]:
    """
    Convert a propositional logic formula to Conjunctive Normal Form (CNF).
    Returns a list of clauses, where each clause is a set of literals.
    """
    tokens = tokenize(formula)
    parsed = parse_formula(tokens)
    
    # Step 1: Eliminate biconditionals (↔)
    no_biconditionals = eliminate_biconditional(parsed)
    
    # Step 2: Eliminate implications (→)
    no_implications = eliminate_implication(no_biconditionals)
    
    # Step 3: Move negations inward
    negations_inward = move_negation_inward(no_implications)
    
    # Step 4: Distribute OR over AND
    cnf_formula = distribute_or_over_and(negations_inward)
    
    # Extract clauses
    return extract_clauses(cnf_formula)


def resolve(clause1: Set[str], clause2: Set[str]) -> Set[FrozenSet[str]]:
    """
    Apply the resolution rule to two clauses.
    Returns a set of clauses that can be derived by resolving clause1 and clause2.
    """
    resolvents = set()
    
    for literal1 in clause1:
        for literal2 in clause2:
            if literal1 == negate(literal2) or negate(literal1) == literal2:
                # Create new clause by resolving on these literals
                new_clause = (clause1.union(clause2) - {literal1, literal2})
                
                # Only add non-tautological clauses
                if not any(lit in new_clause and negate(lit) in new_clause for lit in new_clause):
                    resolvents.add(frozenset(new_clause))
    
    return resolvents


def resolution(clauses: Set[FrozenSet[str]]) -> bool:
    """
    Apply the resolution algorithm to a set of clauses.
    Returns True if the empty clause is derived (indicating a contradiction),
    otherwise returns False.
    """
    new = set()
    
    while True:
        # Generate all possible pairs of clauses
        pairs = [(c1, c2) for c1 in clauses for c2 in clauses if c1 != c2]
        
        for (clause1, clause2) in pairs:
            resolvents = resolve(set(clause1), set(clause2))
            
            if frozenset() in resolvents:  # Empty clause found
                return True
            
            new = new.union(resolvents)
        
        if new.issubset(clauses):  # No new clauses were derived
            return False
        
        clauses = clauses.union(new)


def entails(kb_clauses: List[Set[str]], phi: str) -> bool:
    """
    Check if a knowledge base entails a formula.
    kb_clauses: List of clauses from the knowledge base
    phi: Formula to check entailment for
    Returns True if KB entails phi, False otherwise
    """
    # Convert KB clauses to frozensets
    kb = {frozenset(clause) for clause in kb_clauses}
    
    # Negate phi and convert to CNF
    not_phi = f"~({phi})"
    not_phi_clauses = to_cnf(not_phi)
    not_phi_frozen = {frozenset(clause) for clause in not_phi_clauses}
    
    # Combine KB with negated phi
    all_clauses = kb.union(not_phi_frozen)
    
    # Apply resolution
    return resolution(all_clauses)

def check_entailment(belief_base: BeliefBase, query: str) -> bool:
    # Extract the formulas from the belief base as strings
    kb_formulas = [str(belief.formula) for belief in belief_base.beliefs]

    # Convert each formula into CNF clauses
    kb_clauses = []
    for formula in kb_formulas:
        clauses = to_cnf(formula)
        kb_clauses.extend(clauses)

    # Check if the belief base entails the query
    result = entails(kb_clauses, query)
    
    return result
