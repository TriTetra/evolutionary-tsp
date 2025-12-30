import random
from typing import List, Tuple

def ordered_crossover(parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
    """
    Performs Ordered Crossover (OX1) on two parents.
    
    This operator preserves a subsequence of cities from one parent and fills the 
    remaining spots with cities from the other parent in the order they appear, 
    starting after the second cut point. It is widely used for TSP.

    Args:
        parent1 (List[int]): The first parent route.
        parent2 (List[int]): The second parent route.

    Returns:
        Tuple[List[int], List[int]]: Two new child routes.
    """
    size = len(parent1)
    
    # Select two random cut points
    cxpoint1, cxpoint2 = sorted(random.sample(range(size), 2))
    
    def ox_helper(p1: List[int], p2: List[int]) -> List[int]:
        # Initialize child with placeholders (-1)
        child = [-1] * size
        
        # Copy the sub-tour from p1 to child
        child[cxpoint1:cxpoint2] = p1[cxpoint1:cxpoint2]
        
        # OPTIMIZATION: Use a set for O(1) lookups instead of O(N) list search
        existing_cities = set(child[cxpoint1:cxpoint2])
        
        # Fill the remaining positions using p2
        # Start filling from the index after the second cut point
        current_pos = cxpoint2
        
        # Start scanning p2 from the index after the second cut point
        for i in range(size):
            candidate = p2[(cxpoint2 + i) % size]
            
            # Check if candidate is already in the child (O(1) operation)
            if candidate not in existing_cities:
                
                # Skip the segment that is already filled
                if cxpoint1 <= current_pos < cxpoint2:
                     # Jump to the end of the segment
                    current_pos = cxpoint2
                
                # Wrap around if we reach the end of the array
                if current_pos >= size:
                    current_pos = 0
                    # Re-check if we landed on the reserved segment after wrapping
                    if cxpoint1 <= current_pos < cxpoint2:
                        current_pos = cxpoint2

                child[current_pos] = candidate
                current_pos += 1
                
        return child

    child1 = ox_helper(parent1, parent2)
    child2 = ox_helper(parent2, parent1)
    
    return child1, child2


def cycle_crossover(parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
    """
    Performs Cycle Crossover (CX) on two parents.
    
    CX preserves the absolute position of elements in the sequence. 
    It ensures that each city and its position comes from one of the parents.
    

    Args:
        parent1 (List[int]): The first parent route.
        parent2 (List[int]): The second parent route.

    Returns:
        Tuple[List[int], List[int]]: Two new child routes.
    """
    size = len(parent1)
    
    def cx_helper(p1: List[int], p2: List[int]) -> List[int]:
        # Initialize child with placeholders
        child = [-1] * size
        
        # Create a lookup table for p1 indices to avoid O(N^2) searches
        # value -> index in p1
        p1_indices = {val: i for i, val in enumerate(p1)}
        
        # 1. Identify the first cycle starting at index 0
        cycle_indices = set()
        idx = 0
        
        while idx not in cycle_indices:
            cycle_indices.add(idx)
            val_in_p2 = p2[idx]
            # Find where this value is located in p1 to continue the cycle
            idx = p1_indices[val_in_p2]
        
        # 2. Copy the cities from the cycle from P1 to child
        for i in cycle_indices:
            child[i] = p1[i]
            
        # 3. Fill the remaining positions from P2
        for i in range(size):
            if child[i] == -1:
                child[i] = p2[i]
                
        return child

    child1 = cx_helper(parent1, parent2)
    child2 = cx_helper(parent2, parent1)
    
    return child1, child2