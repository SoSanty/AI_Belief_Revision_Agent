from belief_base import BeliefBase, Atom, And, Or, Not, Implies
from contraction import partial_meet_contraction
import re

# Function to parse the input formula
def parse_input_formula(raw):
    # Tokenize the formula (splits the formula into "tokens")
    tokens = re.findall(r'\w+|<->|->|AND|OR|NOT|\(|\)', raw)
    # Convert the logical keywords AND, OR, NOT to uppercase
    tokens = [t.upper() if t.lower() in {"and", "or", "not"} else t for t in tokens]
    pos = 0  # Current token position

    # Function to parse bi-implication (↔)
    def parse_biimplication():
        nonlocal pos
        # Start by parsing implications (→)
        node = parse_implication()
        # Handles bi-implications (↔) by finding a pattern A ↔ B
        while pos < len(tokens) and tokens[pos] == '<->':
            pos += 1
            node = And(Implies(node, parse_implication()), Implies(parse_implication(), node))
        return node

    # Function to parse implications (→)
    def parse_implication():
        nonlocal pos
        # Start by parsing an expression
        node = parse_expression()
        # Handles implications (→) by finding a pattern A → B
        while pos < len(tokens) and tokens[pos] == '->':
            pos += 1
            node = Implies(node, parse_expression())
        return node

    # Function to parse an expression (OR connective)
    def parse_expression():
        nonlocal pos
        # Start by parsing a term
        node = parse_term()
        # Handles OR (disjunction) by finding a pattern A ∨ B
        while pos < len(tokens) and tokens[pos] == 'OR':
            pos += 1
            node = Or(node, parse_term())
        return node

    # Function to parse a term (AND connective)
    def parse_term():
        nonlocal pos
        # Start by parsing a factor
        node = parse_factor()
        # Handles AND (conjunction) by finding a pattern A ∧ B
        while pos < len(tokens) and tokens[pos] == 'AND':
            pos += 1
            node = And(node, parse_factor())
        return node

    # Function to parse a factor (literals, NOT, or parentheses)
    def parse_factor():
        nonlocal pos
        if tokens[pos] == 'NOT':
            pos += 1
            # Parse the negation of a factor (¬A)
            return Not(parse_factor())
        elif tokens[pos] == '(':
            pos += 1
            # Parse an expression within parentheses
            node = parse_biimplication()
            if tokens[pos] != ')':
                raise ValueError("Expected ')'")
            pos += 1
            return node
        else:
            # It's an atom (propositional variable)
            token = tokens[pos]
            pos += 1
            return Atom(token)

    # Start the parsing process with bi-implication
    result = parse_biimplication()
    
    # Check if there are any unprocessed tokens
    if pos != len(tokens):
        raise ValueError("Unexpected token: " + tokens[pos])
    return result

# Main function that handles user interaction
def main():
    belief_base = BeliefBase()  # Create a new belief base

    while True:
        # Display the menu options
        print("\n=== Belief Revision Agent ===")
        print("1. View belief base")  # Option to view the belief base
        print("2. Expand belief base")  # Option to expand the belief base
        print("3. Contract belief base")  # Option to contract the belief base
        print("4. Exit")  # Option to exit

        # Get the user's choice
        choice = input("Choose an action (1-4): ").strip()

        if choice == "1":
            # Display the belief base
            print(belief_base)

        elif choice == "2":
            # Expand the belief base with a new formula
            raw = input("Enter formula to expand (e.g., A, NOT A, A AND B, A -> B): ")
            try:
                formula = parse_input_formula(raw)  # Parse the formula
                belief_base.expand(formula)  # Expand the belief base
                print("Belief added.")  # Confirm the addition
            except Exception as e:
                print(f"Error: {e}")  # Handle any errors in parsing the formula

        elif choice == "3":
            # Contract the belief base by removing a formula
            raw = input("Enter formula to contract: ")
            try:
                formula = parse_input_formula(raw)  # Parse the formula
                new_beliefs = partial_meet_contraction(belief_base, formula)  # Perform the contraction
                belief_base.beliefs = list(new_beliefs)  # Update the belief base
                print("Belief base contracted.")  # Confirm the contraction
            except Exception as e:
                print(f"Error: {e}")  # Handle any errors in parsing the formula

        elif choice == "4":
            # Exit the program
            print("Goodbye!")
            break

        else:
            # Handle invalid input
            print("Invalid choice. Try again.")

# Run the main function if the program is executed directly
if __name__ == "__main__":
    main()
