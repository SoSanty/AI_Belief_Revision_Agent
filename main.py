from belief_base import BeliefBase, Atom, And, Or, Not, Implies
from contraction import partial_meet_contraction

import re
def parse_input_formula(raw):
    # Tokenize the formula
    tokens = re.findall(r'\w+|<->|->|AND|OR|NOT|\(|\)', raw)
    tokens = [t.upper() if t.lower() in {"and", "or", "not"} else t for t in tokens]
    pos = 0

    def parse_biimplication():
        nonlocal pos
        node = parse_implication()
        while pos < len(tokens) and tokens[pos] == '<->':
            pos += 1
            node = And(Implies(node, parse_implication()), Implies(parse_implication(), node))
        return node

    def parse_implication():
        nonlocal pos
        node = parse_expression()
        while pos < len(tokens) and tokens[pos] == '->':
            pos += 1
            node = Implies(node, parse_expression())
        return node

    def parse_expression():
        nonlocal pos
        node = parse_term()
        while pos < len(tokens) and tokens[pos] == 'OR':
            pos += 1
            node = Or(node, parse_term())
        return node

    def parse_term():
        nonlocal pos
        node = parse_factor()
        while pos < len(tokens) and tokens[pos] == 'AND':
            pos += 1
            node = And(node, parse_factor())
        return node

    def parse_factor():
        nonlocal pos
        if tokens[pos] == 'NOT':
            pos += 1
            return Not(parse_factor())
        elif tokens[pos] == '(':
            pos += 1
            node = parse_biimplication()
            if tokens[pos] != ')':
                raise ValueError("Expected ')'")
            pos += 1
            return node
        else:
            token = tokens[pos]
            pos += 1
            return Atom(token)

    result = parse_biimplication()
    if pos != len(tokens):
        raise ValueError("Unexpected token: " + tokens[pos])
    return result

def main():
    belief_base = BeliefBase()

    while True:
        print("\n=== Belief Revision Agent ===")
        print("1. View belief base")
        print("2. Expand belief base")
        print("3. Contract belief base")
        print("4. Exit")

        choice = input("Choose an action (1-4): ").strip()

        if choice == "1":
            print("\nCurrent Belief Base:")
            print(belief_base)

        elif choice == "2":
            raw = input("Enter formula to expand (e.g., A, NOT A, A AND B, A -> B): ")
            try:
                formula = parse_input_formula(raw)
                belief_base.expand(formula)
                print("Belief added.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "3":
            raw = input("Enter formula to contract: ")
            try:
                formula = parse_input_formula(raw)
                new_beliefs = partial_meet_contraction(belief_base, formula)
                belief_base.beliefs = list(new_beliefs)
                print("Belief base contracted.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()