from itertools import chain, combinations
from belief_base import *
from partB import * 

# Generate the powerset of a set
def powerset(s):
    """
    Returns all possible subsets (the power set) of the given set 's'.
    Useful for computing all candidate belief subsets.
    """
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

# Calculate the total priority of a subset of beliefs
def total_priority(subset):
    """
    Returns the total priority of a subset of beliefs.
    Each belief has an associated priority, which is summed here.
    """
    return sum(belief.priority for belief in subset)

# Check if a belief subset is a *maximal* subset that does NOT entail the formula
def is_maximal_non_entailing(subset, full_base, formula):
    """
    Determines whether 'subset' does NOT entail 'formula' and is maximal w.r.t. this property.
    I.e., you cannot add more beliefs from 'full_base' without causing entailment of 'formula'.
    """
    # If the current subset entails the formula, it's not valid
    if entails(subset, formula):
        return False
    # Check that no strictly larger subset (of full_base) also avoids entailment
    for other in powerset(full_base):
        other = set(other)
        if set(subset) < other and not entails(other, formula):
            return False
    return True

# Compute all remainders of the belief base w.r.t. the formula
#def compute_remainders(belief_base, formula):
#    """
#    Computes all 'remainders' of the belief base after contracting by 'formula'.
#    A remainder is a maximal subset that does not entail 'formula'.
#    """
#    remainders = []
#    for subset in powerset(belief_base.beliefs):
#        subset = set(subset)
#        if is_maximal_non_entailing(subset, belief_base.beliefs, formula):
#            remainders.append(subset)
#    return remainders

def compute_remainders(belief_base, formula):
    """
    Computes all 'remainders' of the belief base after contracting by 'formula'.
    A remainder is a maximal subset that does not entail 'formula'.
    """
    remainders = []
    beliefs = list(belief_base.beliefs)
    print("\n--- Computing Remainders ---")
    print(f"Formula to contract (¬entail): {formula}")
    print(f"Beliefs in base: {[b.formula for b in beliefs]}")

    for subset in powerset(beliefs):
        subset = set(subset)

        try:
            result = entails(subset, formula)
        except Exception as e:
            print(f"Error in entailment check: {e}")
            continue

        print(f"Testing subset: {[str(b.formula) for b in subset]}")
        print(f" -> Entails {formula}? {result}")

        if is_maximal_non_entailing(subset, beliefs, formula):
            print(" --> ✅ Valid remainder (maximal & non-entailing)\n")
            remainders.append(subset)
        else:
            print(" --> ❌ Rejected (not maximal or entails formula)\n")

    print(f"\nTotal valid remainders found: {len(remainders)}\n")
    
    return remainders


# Select best remainders using priorities and minimal information loss
def select_remainders_by_priority(remainders):
    """
    Selects among the remainders those with the highest total priority.
    Among those, keeps only the ones with the largest number of beliefs (minimal information loss).
    """
    if not remainders:
        return []

    # Pair each remainder with its total priority score
    scored = [(subset, total_priority(subset)) for subset in remainders]
    
    # Get maximum priority score
    max_priority = max(score for _, score in scored)
    
    # Filter remainders that have this maximum score
    top_priority_subsets = [subset for subset, score in scored if score == max_priority]

    # Among them, keep the largest ones (by belief count)
    max_len = max(len(s) for s in top_priority_subsets)
    best_remainders = [s for s in top_priority_subsets if len(s) == max_len]
    
    return best_remainders

# Main contraction function (partial meet contraction)
def partial_meet_contraction(belief_base, formula):
    """
    Performs partial meet contraction of the belief base with respect to 'formula'.
    It removes just enough beliefs to ensure 'formula' is no longer entailed,
    keeping as much high-priority information as possible.
    """
    remainders = compute_remainders(belief_base, formula)
    
    if not remainders:
        print("No valid remainders found. Returning the original belief base.")
        return belief_base.beliefs

    selected = select_remainders_by_priority(remainders)
    
    # The contraction result is the intersection of the selected remainders
    contracted = set.intersection(*map(set, selected))
    
    return contracted

# Check logical entailment of a formula from a list of formulas
def entails(beliefs, formula):
    """
    beliefs: a set of Belief objects
    formula: a Formula object
    """
    bb = BeliefBase()
    for belief in beliefs:
        bb.expand(belief.formula, belief.priority)
    return check_entailment(bb, formula)