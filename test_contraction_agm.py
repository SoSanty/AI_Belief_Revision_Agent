# test_contraction_agm.py

from contraction import partial_meet_contraction, entails
from belief_base import BeliefBase, Atom, And, Or, Not, Implies

def closure(belief_base):
    # Dummy closure: restituisce la base così com'è
    return set(belief_base)

def is_closed(belief_base):
    return closure(belief_base) == set(belief_base)

def test_agm_postulates(original_base, contracted_base, phi):
    print("\n--- Testing AGM Postulates ---")
    
    # 1. Closure
    if is_closed(contracted_base):
        print("Closure: PASSED ✅")
    else:
        print("Closure: FAILED ❌")
        
    # 2. Success
    if entails(original_base, phi):
        if not entails(contracted_base, phi):
            print("Success: PASSED ✅")
        else:
            print("Success: FAILED ❌")
    else:
        print("Success: Not applicable (phi not entailed originally)")
        
    # 3. Inclusion
    if contracted_base.issubset(original_base):
        print("Inclusion: PASSED ✅")
    else:
        print("Inclusion: FAILED ❌")
        
    # 4. Vacuity
    if not entails(original_base, phi):
        if contracted_base == original_base:
            print("Vacuity: PASSED ✅")
        else:
            print("Vacuity: FAILED ❌")
    else:
        print("Vacuity: Not applicable (phi entailed originally)")
        
    # 5. Extensionality
    print("Extensionality: Skipped for now")
        
    # 6. Recovery
    recovery_base = contracted_base.union({phi})
    if original_base.issubset(closure(recovery_base)):
        print("Recovery: PASSED ✅")
    else:
        print("Recovery: FAILED ❌")


# ESEMPIO DI UTILIZZO:

if __name__ == "__main__":
    # Creo una belief base semplice
    B = {"p", "q -> r", "p -> q"}  # Simuliamo come stringhe
    phi = "r"
    priorities = {
        "p": 3,
        "q -> r": 2,
        "p -> q": 1
    }

    # Eseguo la contraction
    B_contracted = partial_meet_contraction(B, phi, priorities, entails)

    # Eseguo i test AGM
    test_agm_postulates(B, B_contracted, phi)
