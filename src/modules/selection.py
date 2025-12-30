import numpy as np
import random
from typing  import List


def tournament_selection (population: List[List[int]], scores: List[float], num_parents: int, k: int = 3) -> List[List[int]]:
    """
    Tournament Selection.

    Selects 'k' individuals randomly from the population and takes the best one (the one with the shortest distance).
    Repeats this process as many times as 'num_parents'.

    Args:
    population (List[List[int]]): List of routes.
    scores (List[float]): Distance of each route (Lower is better).
    num_parents (int): Total number of parents to select.
    k (int): Tournament size. Usually 3 or 5 are used.

    Returns:
    List[List[int]]: List of selected parents.
    """
    selected_parents = []
    pop_size = len(population)

    # Instead of looping through Python lists, we iterate through indexes.
    # This method is lighter than constantly copying the 'population' list.
    for _ in range(num_parents):
        # Randomly select k indexs
        contender_indices = random.sample(range(pop_size), k)

        # Find the best (lowest score) among these indices. 
        # We use min() because scores[i] is the distance to be minimized.
        best_idx = min(contender_indices, key=lambda idx: scores[idx])

        selected_parents.append(population[best_idx])

    return selected_parents


def roulette_wheel_selection(population: List[List[int]], scores: List[float], num_parents: int) -> List[List[int]]:
    """
    Roulette Wheel Selection (Fitness Proportional Selection).

    Individuals with better scores (lower distances) have a higher chance of being selected.
    Since TSP is a minimization problem, the transformation Fitness = 1 / Distance is used.

    Includes NumPy optimization: Calculates probabilities once and performs a bulk selection.

    Args:
    population: Routes.
    scores: Distances.
    num_parents: Desired number of parents.

    Returns:
    Selected parents.
    """

    scores_np = np.array(scores)

    # 1. Fitness Conversion: The shorter the distance, the higher the fitness should be. 
    # We can add epsilon (1e-6) to avoid the division by zero error, but in TSP the distance is not 0.
    fitness_values = 1.0 / scores_np

    # 2. Probability Distribution: Each individual's share of the pie
    total_fitness = np.sum(fitness_values)
    probabilities = fitness_values / total_fitness

    # 3. Bulk Selection (This is where NumPy's power comes in)
    # replace=True: The same individual can be selected as parent more than once (This is normal for genetic diversity)
    selected_indices = np.random.choice(len(population), size=num_parents, p=probabilities, replace=True)

    result = []
    for i in selected_indices:
        result.append(population[i])

    return result


def rank_based_selection(population: List[List[int]], scores: List[float], num_parents: int) -> List[List[int]]:
    """
    Rank Selection.

    It looks at individuals' rankings, not their score values.
    This balances the selection if fitness values ​​are very close or if one is overly dominant.

    The best individual gets N points, the worst individual gets 1 point.

    Args:
    population: Routes.
    scores: Distances.
    num_parents: Desired number of parents.
    """
    pop_size = len(population)
    
    # 1. Sorting: Sort the indexes by scores (Small to large - Best first)
    # The argsort() function gives us the sorted indexes
    sorted_indices = np.argsort(scores) 
    
    # 2. Rank Assignment:

    # sorted_indices[0] (Best) -> Rank: pop_size (Highest chance)
    # sorted_indices[-1] (Worst) -> Rank: 1 (Lowest chance)

    # We create a rank sequence from worst to best.
    # However, since our sorted_indices are based on scores, not "Best -> Worst",
    # scores[sorted_indices[0]] means the shortest distance (best). # So the ranking is: Good -> Bad.
    # The rank points we will assign should be: N, N-1, ..., 1.
    
    ranks = np.arange(pop_size, 0, -1) # [N, N-1, ..., 1]
    
    # 3. Probability Calculation
    total_rank = np.sum(ranks)
    probabilities = ranks / total_rank
    
    # 4. Selection (we will make the selection via sorted_indices)
    # We decide which rank index we will select.
    selected_rank_indices = np.random.choice(pop_size, size=num_parents, p=probabilities, replace=True)
    
    # Conversion of selected ranks to actual population indices
    final_indices = sorted_indices[selected_rank_indices]

    result = []
    for idx in final_indices:
        value = population[idx]
        result.append(value)

    return result