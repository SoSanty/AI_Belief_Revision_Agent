import itertools

class Belief:
    def __init__(self, formula, priority=0):
        self.formula = formula
        self.priority = priority

    def __str__(self):
        return f"{self.formula} [priority={self.priority:.2f}]"
    def __repr__(self):
        return f"Belief({repr(self.formula)}, priority={self.priority})"

    def evaluate(self, model):
        return self.formula.evaluate(model)

    def get_atoms(self):
        return self.formula.get_atoms()

class BeliefBase:
    def __init__(self):
        self.beliefs = []
        self.belief_counter = 0

    def expand(self, formula, priority=0):
        if priority == 0:
            # More recent formulas (added later) get higher priority
            recency_score = self.belief_counter
            simplicity_score = 1 / (len(str(formula)) + 1)  # Shorter formulas get more points
            priority = (5 * recency_score) + (3 * simplicity_score)
    
        self.beliefs.append(Belief(formula, priority))

        if not self.is_consistent():
            print(f"Warning: By adding {formula} you've made the belief base inconsistent.")

        self.belief_counter += 1
    def __str__(self):
        status = "Consistent" if self.is_consistent() else "Inconsistent"
        beliefs_str = " , ".join(str(belief) for belief in self.beliefs)
        return f"Belief Base: {beliefs_str}\nStatus: {status}"

    def __repr__(self):
        return f"BeliefBase({self.beliefs})"
    
    def evaluate_all(self, model):
        return all(belief.evaluate(model) for belief in self.beliefs)
    
    def evaluate_any(self, model):
        return any(belief.evaluate(model) for belief in self.beliefs)
    
    def get_atoms(self):
        atoms = set()
        for belief in self.beliefs:
            atoms.update(belief.get_atoms())
        return atoms
    
    def generate_all_models(self):
        atoms = sorted(self.get_atoms())
        truth_combinations = itertools.product([True, False], repeat=len(atoms))
        
        models = []
        for combo in truth_combinations:
            model = dict(zip(atoms, combo))
            models.append(model)
        
        return models

    def is_consistent(self):
        for model in self.generate_all_models():
            if self.evaluate_all(model):
                return True  # At least one model satisfies all beliefs
        return False  # No model satisfies all beliefs

class Atom:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Atom('{self.name}')"
    
    def evaluate(self, model):
        return model[self.name]
    
    def get_atoms(self):
        return {self.name}

class And:
    def __init__(self, *args):
        self.operands = args

    def __str__(self):
        return "(" + " ∧ ".join(str(op) for op in self.operands) + ")"

    def __repr__(self):
        return f"And({', '.join(repr(op) for op in self.operands)})"
    
    def evaluate(self, model):
        return all(op.evaluate(model) for op in self.operands)
    
    def get_atoms(self):
        atoms = set()
        for operand in self.operands:
            if isinstance(operand, Atom):
                atoms.add(operand.name)
            elif isinstance(operand, (And, Or, Not, Implies)):
                atoms.update(operand.get_atoms())
        return atoms

class Or:
    def __init__(self, *args):
        self.operands = args

    def __str__(self):
        return "(" + " ∨ ".join(str(op) for op in self.operands) + ")"

    def __repr__(self):
        return f"Or({', '.join(repr(op) for op in self.operands)})"
    
    def evaluate(self, model):
        return any(op.evaluate(model) for op in self.operands)
    
    def get_atoms(self):
        atoms = set()
        for operand in self.operands:
            if isinstance(operand, Atom):
                atoms.add(operand.name)
            elif isinstance(operand, (And, Or, Not, Implies)):
                atoms.update(operand.get_atoms())
        return atoms

class Not:
    def __init__(self, operand):
        self.operand = operand

    def __str__(self):
        return f"¬{self.operand}"

    def __repr__(self):
        return f"Not({repr(self.operand)})"
    
    def evaluate(self, model):
        return not self.operand.evaluate(model)
    
    def get_atoms(self):
        atoms = set()
        if isinstance(self.operand, Atom):
            atoms.add(self.operand.name)
        elif isinstance(self.operand, (And, Or, Not, Implies)):
            atoms.update(self.operand.get_atoms())
        return atoms

class Implies:
    def __init__(self, antecedent, consequent):
        self.antecedent = antecedent
        self.consequent = consequent

    def __str__(self):
        return f"({self.antecedent} → {self.consequent})"

    def __repr__(self):
        return f"Implies({repr(self.antecedent)}, {repr(self.consequent)})"
    
    def evaluate(self, model):
        return not self.antecedent.evaluate(model) or self.consequent.evaluate(model)
    
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
    


class Biconditional:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return f"({self.left} ↔ {self.right})"

    def __repr__(self):
        return f"Biconditional({repr(self.left)}, {repr(self.right)})"

    def evaluate(self, model):
        return self.left.evaluate(model) == self.right.evaluate(model)

    def get_atoms(self):
        return self.left.get_atoms().union(self.right.get_atoms())
