import itertools

# Class representing a belief, which consists of a formula and an associated priority
class Belief:
    def __init__(self, formula, priority=0):
        self.formula = formula  # The logical formula representing the belief
        self.priority = priority  # The priority of the belief

    # String representation of the belief (used for printing)
    def __str__(self):
        return f"{self.formula} [priority={self.priority:.2f}]"

    # Official string representation of the belief for debugging
    def __repr__(self):
        return f"Belief({repr(self.formula)}, priority={self.priority})"

    # Evaluate the belief based on a given model
    def evaluate(self, model):
        return self.formula.evaluate(model)

    # Get all the atomic propositions involved in the belief
    def get_atoms(self):
        return self.formula.get_atoms()

# Class representing a collection of beliefs (a belief base)
class BeliefBase:
    def __init__(self):
        self.beliefs = []  # List of beliefs in the belief base
        self.belief_counter = 0  # Counter to track the order of belief additions

    # Expand the belief base by adding a new belief, optionally specifying its priority
    def expand(self, formula, priority=0):
        if priority == 0:
            # If no priority is given, calculate a priority based on recency and simplicity
            recency_score = self.belief_counter
            simplicity_score = 1 / (len(str(formula)) + 1)  # Shorter formulas get more points
            priority = (5 * recency_score) + (3 * simplicity_score)
    
        # Add the belief to the belief base
        self.beliefs.append(Belief(formula, priority))

        # Check if the belief base is consistent after adding the new belief
        if not self.is_consistent():
            print(f"Warning: By adding {formula} you've made the belief base inconsistent.")

        self.belief_counter += 1

    # String representation of the belief base (used for printing)
    def __str__(self):
        status = "Consistent" if self.is_consistent() else "Inconsistent"
        beliefs_str = " , ".join(str(belief) for belief in self.beliefs)
        return f"Belief Base: {beliefs_str}\nStatus: {status}"

    # Official string representation of the belief base for debugging
    def __repr__(self):
        return f"BeliefBase({self.beliefs})"
    
    # Evaluate all beliefs in the belief base for a given model
    def evaluate_all(self, model):
        return all(belief.evaluate(model) for belief in self.beliefs)
    
    # Evaluate if any belief in the belief base is true for a given model
    def evaluate_any(self, model):
        return any(belief.evaluate(model) for belief in self.beliefs)
    
    # Get all atomic propositions involved in the belief base
    def get_atoms(self):
        atoms = set()
        for belief in self.beliefs:
            atoms.update(belief.get_atoms())
        return atoms
    
    # Generate all possible models (truth assignments) based on the atomic propositions
    def generate_all_models(self):
        atoms = sorted(self.get_atoms())  # Sort atoms to ensure consistent order
        truth_combinations = itertools.product([True, False], repeat=len(atoms))
        
        models = []
        for combo in truth_combinations:
            model = dict(zip(atoms, combo))  # Create a truth assignment model
            models.append(model)
        
        return models

    # Check if the belief base is consistent (there exists at least one model that satisfies all beliefs)
    def is_consistent(self):
        for model in self.generate_all_models():
            if self.evaluate_all(model):
                return True  # At least one model satisfies all beliefs
        return False  # No model satisfies all beliefs

# Class representing an atomic proposition (e.g., A, B, etc.)
class Atom:
    def __init__(self, name):
        self.name = name  # Name of the atomic proposition

    # String representation of the atom
    def __str__(self):
        return self.name

    # Official string representation of the atom for debugging
    def __repr__(self):
        return f"Atom('{self.name}')"
    
    # Evaluate the atom based on a given model (returning its truth value)
    def evaluate(self, model):
        return model[self.name]
    
    # Get the atoms that appear in the atomic proposition (itself)
    def get_atoms(self):
        return {self.name}

# Class representing the logical AND (conjunction) operator
class And:
    def __init__(self, *args):
        self.operands = args  # Operands (sub-formulas) involved in the AND operation

    # String representation of the AND operation
    def __str__(self):
        return "(" + " ∧ ".join(str(op) for op in self.operands) + ")"

    # Official string representation of the AND operation for debugging
    def __repr__(self):
        return f"And({', '.join(repr(op) for op in self.operands)})"
    
    # Evaluate the AND operation for a given model
    def evaluate(self, model):
        return all(op.evaluate(model) for op in self.operands)
    
    # Get all atoms involved in the AND operation
    def get_atoms(self):
        atoms = set()
        for operand in self.operands:
            if isinstance(operand, Atom):
                atoms.add(operand.name)
            elif isinstance(operand, (And, Or, Not, Implies)):
                atoms.update(operand.get_atoms())
        return atoms

# Class representing the logical OR (disjunction) operator
class Or:
    def __init__(self, *args):
        self.operands = args  # Operands (sub-formulas) involved in the OR operation

    # String representation of the OR operation
    def __str__(self):
        return "(" + " ∨ ".join(str(op) for op in self.operands) + ")"

    # Official string representation of the OR operation for debugging
    def __repr__(self):
        return f"Or({', '.join(repr(op) for op in self.operands)})"
    
    # Evaluate the OR operation for a given model
    def evaluate(self, model):
        return any(op.evaluate(model) for op in self.operands)
    
    # Get all atoms involved in the OR operation
    def get_atoms(self):
        atoms = set()
        for operand in self.operands:
            if isinstance(operand, Atom):
                atoms.add(operand.name)
            elif isinstance(operand, (And, Or, Not, Implies)):
                atoms.update(operand.get_atoms())
        return atoms

# Class representing the logical NOT (negation) operator
class Not:
    def __init__(self, operand):
        self.operand = operand  # Operand involved in the NOT operation

    # String representation of the NOT operation
    def __str__(self):
        return f"¬{self.operand}"

    # Official string representation of the NOT operation for debugging
    def __repr__(self):
        return f"Not({repr(self.operand)})"
    
    # Evaluate the NOT operation for a given model
    def evaluate(self, model):
        return not self.operand.evaluate(model)
    
    # Get all atoms involved in the NOT operation
    def get_atoms(self):
        atoms = set()
        if isinstance(self.operand, Atom):
            atoms.add(self.operand.name)
        elif isinstance(self.operand, (And, Or, Not, Implies)):
            atoms.update(self.operand.get_atoms())
        return atoms

# Class representing the logical IMPLIES (implication) operator
class Implies:
    def __init__(self, antecedent, consequent):
        self.antecedent = antecedent  # The antecedent (the "if" part)
        self.consequent = consequent  # The consequent (the "then" part)

    # String representation of the IMPLIES operation
    def __str__(self):
        return f"({self.antecedent} → {self.consequent})"

    # Official string representation of the IMPLIES operation for debugging
    def __repr__(self):
        return f"Implies({repr(self.antecedent)}, {repr(self.consequent)})"
    
    # Evaluate the IMPLIES operation for a given model
    def evaluate(self, model):
        return not self.antecedent.evaluate(model) or self.consequent.evaluate(model)
    
    # Get all atoms involved in the IMPLIES operation
    def get_atoms(self):
        atoms = set()
        if isinstance(self.antecedent, Atom):
            atoms.add(self.antecedent.name)
        elif isinstance(self.antecedent, (And, Or, Not, Implies)):
            atoms.update(self.antecedent.get_atoms())
        if isinstance(self.consequent, Atom):
            atoms.add(self.consequent.name)
        elif isinstance(self.consequent, (And, Or, Not, Implies)):
            atoms.update(self.consequent.get_atoms())
        return atoms

# Class representing the logical BICONDITIONAL (↔) operator
class Biconditional:
    def __init__(self, left, right):
        self.left = left  # Left operand (the "if and only if" part)
        self.right = right  # Right operand (the other part)

    # String representation of the BICONDITIONAL operation
    def __str__(self):
        return f"({self.left} ↔ {self.right})"

    # Official string representation of the BICONDITIONAL operation for debugging
    def __repr__(self):
        return f"Biconditional({repr(self.left)}, {repr(self.right)})"

    # Evaluate the BICONDITIONAL operation for a given model
    def evaluate(self, model):
        return self.left.evaluate(model) == self.right.evaluate(model)

    # Get all atoms involved in the BICONDITIONAL operation
    def get_atoms(self):
        return self.left.get_atoms().union(self.right.get_atoms())

