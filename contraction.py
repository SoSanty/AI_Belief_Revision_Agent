from itertools import chain, combinations

# Dummy entailment function to be replaced with your real one
def entails(belief_base, formula):
    """
    Check if belief_base logically entails formula.
    Replace with resolution/CNF method from your teammates.
    """
    # Example dummy logic: check if formula is in the base
    return formula in belief_base

# Generate all subsets of a set
def powerset(s):
    """Returns all subsets of a set s."""
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

# Check if a subset is a maximal non-entailing subset
def is_maximal_non_entailing(subset, full_base, formula, entails):
    subset = set(subset)
    if entails(subset, formula):
        return False
    for other in powerset(full_base):
        other = set(other)
        if subset < other and not entails(other, formula):
            return False
    return True

# Find all remainder sets
def compute_remainders(belief_base, formula, entails):
    remainders = []
    for subset in powerset(belief_base):
        subset = set(subset)
        if is_maximal_non_entailing(subset, belief_base, formula, entails):
            remainders.append(subset)
    return remainders

# Selection function for remainder sets (full meet)
def select_remainders(remainders):
    return remainders  # could customize here with ranking

# Partial meet contraction logic
def partial_meet_contraction(belief_base, formula, entails):
    remainders = compute_remainders(belief_base, formula, entails)
    if not remainders:
        print("No valid remainder sets found. Returning original belief base.")
        return belief_base
    selected = select_remainders(remainders)
    contracted = set.intersection(*selected)
    return contracted

# Entry point function to use the contraction tool
def main():
    print("=== Belief Base Contraction Tool ===")
    
    # Get belief base input
    base_input = input("Enter belief base formulas separated by commas: ")
    belief_base = set(map(str.strip, base_input.split(",")))

    # Get formula to contract
    formula = input("Enter the formula to contract (φ): ").strip()

    print("\nOriginal Belief Base:")
    print(belief_base)
    print("Formula to contract:", formula)

    # Perform contraction
    contracted = partial_meet_contraction(belief_base, formula, entails)

    print("\nContracted Belief Base:")
    print(contracted)

# Run script
if __name__ == "__main__":
    main()
