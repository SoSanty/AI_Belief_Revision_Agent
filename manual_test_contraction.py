# Import necessary modules and functions
# from contraction import partial_meet_contraction, entails  # (alternative import if using different module names)
from belief_base import *
from BeliefBaseContraction import *  # Contains the partial meet contraction logic

# --- Step 1: Build the belief base ---

# Define propositional atoms
p = Atom("P")
q = Atom("Q")
r = Atom("R")

# Define formulas (implications between atoms)
p_implies_q = Implies(p, q)  # P → Q
q_implies_r = Implies(q, r)  # Q → R

# Create an empty belief base
bb = BeliefBase()

# Add beliefs to the base along with their associated priorities (higher = more important)
bb.expand(p)               # Belief: P with priority 4
bb.expand(p_implies_q)     # Belief: P → Q with priority 3
bb.expand(q_implies_r)     # Belief: Q → R with priority 2
bb.expand(r)               # Belief: R with priority 1 (least important)

# --- Step 2: Specify the formula to contract ---

#phi = q  # We want to remove R (i.e., ensure R is no longer entailed)
#phi = r
phi = p
# --- Step 3: Apply partial meet contraction ---

# This will remove the minimal amount of lower-priority beliefs needed
# so that φ (here R) is no longer a logical consequence of the belief base.
contracted = partial_meet_contraction(bb, phi)

# --- Step 4: Output the results ---

print("Original Beliefs:")
for b in bb.beliefs:
    print("-", b)

print("\nFormula to contract (φ):", phi)

print("\nContracted Belief Base:")
for b in contracted:
    print("-", b)

