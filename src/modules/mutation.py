import random
from typing import List

def swap_mutation(route: List[int], mutation_rate: float) -> List[int]:
    """
    Performs Swap Mutation.
    
    Two cities are randomly selected and their positions are swapped.
    This introduces small variations in the route.

    Args:
        route (List[int]): The route to mutate.
        mutation_rate (float): Probability of mutation occurring.

    Returns:
        List[int]: The mutated route (or original if no mutation occurred).
    """
    if random.random() < mutation_rate:
        size = len(route)
        i, j = random.sample(range(size), 2)
        route[i], route[j] = route[j], route[i]
    return route



def insert_mutation(route: List[int], mutation_rate: float) -> List[int]:
    """
    Performs Insert Mutation.
    
    A city is removed from a random position and re-inserted into another random position.
    This changes the adjacency of cities more aggressively than swap.

    Args:
        route (List[int]): The route to mutate.
        mutation_rate (float): Probability of mutation occurring.

    Returns:
        List[int]: The mutated route.
    """
    if random.random() < mutation_rate:
        size = len(route)
        i, j = random.sample(range(size), 2)
        
        # Remove the city at index i
        city = route.pop(i)
        
        # Insert it at index j
        # Note: If j was originally greater than i, the index shifts by -1 after pop.
        # However, random.sample handles distinct indices, and insert handles boundaries.
        route.insert(j, city)
        
    return route



def inversion_mutation(route: List[int], mutation_rate: float) -> List[int]:
    """
    Performs Inversion Mutation (also known as Reverse Mutation).
    
    A sub-segment of the route is selected and reversed.
    This is very effective for TSP as it mimics a random 2-Opt move, 
    fixing "crossing" edges.

    Args:
        route (List[int]): The route to mutate.
        mutation_rate (float): Probability of mutation occurring.

    Returns:
        List[int]: The mutated route.
    """
    if random.random() < mutation_rate:
        size = len(route)
        # Select two cut points
        i, j = sorted(random.sample(range(size), 2))
        
        # Reverse the segment between i and j (inclusive/exclusive logic)
        # Python slicing [i:j+1] includes j.
        route[i:j+1] = route[i:j+1][::-1]
        
    return route