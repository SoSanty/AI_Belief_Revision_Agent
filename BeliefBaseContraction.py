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
    if entails([b.formula for b in subset], formula):
        return False
    # Check that no strictly larger subset (of full_base) also avoids entailment
    for other in powerset(full_base):
        other = set(other)
        if set(subset) < other and not entails([b.formula for b in other], formula):
            return False
    return True

# Compute all remainders of the belief base w.r.t. the formula
def compute_remainders(belief_base, formula):
    """
    Computes all 'remainders' of the belief base after contracting by 'formula'.
    A remainder is a maximal subset that does not entail 'formula'.
    """
    remainders = []
    for subset in powerset(belief_base.beliefs):
        subset = set(subset)
        if is_maximal_non_entailing(subset, belief_base.beliefs, formula):
            remainders.append(subset)
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
def entails(formulas, formula_str):
    """
    Returns True if the given list of formulas logically entails 'formula_str'.
    Uses an auxiliary belief base and a separate entailment checker.
    """
    bb = BeliefBase()
    for f in formulas:
        bb.expand(f)
    return check_entailment(bb, formula_str)
