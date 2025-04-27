from itertools import chain, combinations


"""
Key Components of the Code:

    Entailment Function (entails):

        This function checks if a given belief base logically entails a formula. In the provided code,
        it's a dummy function that just checks if the formula is directly present in the belief base.
        In a full implementation, you would replace this with an actual logical entailment check,
        such as using resolution or checking satisfiability via CNF (Conjunctive Normal Form).

    Powerset Generation (powerset):

        The function powerset(s) generates all subsets of a set s. This is important because, in a meet contraction,
        you need to consider all possible subsets of the belief base to find which ones entail the formula (phi) or not.

    Maximal Non-Entailing Subset Check (is_maximal_non_entailing):

        This function checks whether a given subset is a "maximal" non-entailing subset. A subset is considered maximal if:

            It does not entail the formula phi.

            No superset of this subset (in the powerset of the full belief base) is a valid non-entailing subset.

        This function is key in identifying which subsets are still consistent with the belief base after removing the formula phi.

    Compute Remainders (compute_remainders):

        This function iterates over all subsets of the belief base and collects all subsets that are maximal non-entailing
        (i.e., subsets that don't imply the formula phi). These subsets represent the possible "remainders" after removing the formula.

    Selection Function (select_remainders):

        This function simply returns all the maximal non-entailing subsets (or "remainders").
        The code mentions that you could customize this function with a ranking method,
        which could allow for a more selective contraction strategy (e.g., picking subsets based on priority).

    Partial Meet Contraction (partial_meet_contraction):

        This is the main logic that computes the contraction:

            It first finds all the maximal non-entailing remainders using compute_remainders.

            If no remainders are found, it returns the original belief base (this is a safeguard in case the contraction isn't possible).

            If remainders are found, it selects them (this is done using the select_remainders function) and
            then calculates the intersection of all selected remainders. The intersection of the remainders represents
            the contracted belief base, as it contains only the beliefs that are consistent with the formula removal.

How it Works:

    Input:

        The user provides a set of beliefs (the belief base) and the formula phi they wish to contract.

    Process:

        The program computes all subsets of the belief base.

        For each subset, it checks whether it entails the formula phi.

        The subsets that do not entail phi are considered as candidates.

        Among these, the maximal subsets are chosen — meaning, those that can't be extended further without beginning to entail phi.

    Output:

        The program then calculates the intersection of all maximal non-entailing subsets, which represents the contracted belief base.
        This contraction removes the formula phi while preserving as much of the belief base as possible.
"""



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

# Function to calculate the total priority of a subset
def total_priority(subset, priorities):
    """It calculate the total sum of priority of a subset."""
    return sum(priorities.get(formula, 0) for formula in subset)

# Check if a subset is a maximal non-entailing the belief to contract
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

# Selection function for remainder sets depeding on priority
def select_remainders_by_priority(remainders, priorities):
    # order the remainders by their total priority
    remainders_sorted = sorted(remainders, key=lambda subset: total_priority(subset, priorities), reverse=True)
    return remainders_sorted

# Partial meet contraction logic
def partial_meet_contraction(belief_base, formula, priorities, entails):
    remainders = compute_remainders(belief_base, formula, entails)
    if not remainders:
        print("No valid remainder sets found. Returning original belief base.")
        return belief_base
    selected = select_remainders_by_priority(remainders,priorities)
    contracted = set.intersection(*map(set, selected))
    return contracted

# Entry point function to use the contraction tool
def main():
    print("=== Belief Base Contraction Tool ===")
    
    # Get belief base input
    base_input = input("Enter belief base formulas separated by commas: ")
    belief_base = set(map(str.strip, base_input.split(",")))

    # Get formula to contract
    formula = input("Enter the formula to contract (φ): ").strip()


    priorities_input = input("Inserisci le priorità delle formule come dizionario (esempio: {'p': 3, 'q': 2}): ")
    priorities = eval(priorities_input)


    print("\nOriginal Belief Base:")
    print(belief_base)
    print("Formula to contract:", formula)

    # Perform contraction
    contracted = partial_meet_contraction(belief_base, formula, priorities, entails)

    print("\nContracted Belief Base:")
    print(contracted)

# Run script
if __name__ == "__main__":
    main()
