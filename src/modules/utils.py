import math
import numpy as np
from typing import List, Tuple
from .models import City


def read_tsp_file(filename:str) -> List[City]:

    """
    Args:
        filename (str): .tsp file path.
        
    Returns:
        List[City]: The cities a readen from file.
    """

    cities = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        with open(filename, 'r', encoding='latin-1') as f:
            lines = f.readlines()

    # Reading loop of file
    in_section = False
    for line in lines:
        line = line.strip()

        # Start 
        if line == "NODE_COORD_SECTION":
            in_section = True
            continue
        
        # End
        if line == "EOF":
            break

        # append the cities
        if in_section:
            parts = line.split()

            if len(parts) >= 3:
                try:
                    c_id = int(float(parts[0]))
                    x = float(parts[1])
                    y = float(parts[2])
                    cities.append(City(id=c_id, x=x, y=y))
                except ValueError:
                    continue # Pass the wrong lines

    return cities


def compute_distance_matrix(cities: List[City]) -> np.ndarray:
    """
    Its calculates NxN euclid distance matrix for given cities.
    
    
    It is very fast because it uses NumPy broadcasting instead of Python loops.
    It performs O(N^2) operations, but because it operates at the C level, it takes seconds.
    
    Args:
        cities (List[City]): Nested City List.
        
    Returns:
        np.ndarray: a 2D array where matrix[i][j] gives the distance between cities i and j.
    """
    n = len(cities)

    # converting the coords to the numpy array
    coords_list = []
    for c in cities:
        coords_list.append((c.x, c.y))

    coords_list = np.array(coords_list, dtype=np.float64)

    # # Find the difference between all pairs using Broadcasting: (x1-x2, y1-y2)
    deltas = coords_list[:, np.newaxis, :] - coords_list[np.newaxis, :, :]

    dists = np.sqrt(np.sum(deltas**2, axis=-1))

    return dists


def calculate_route_distance(route: List[int], distance_matrix: np.ndarray) -> float:
    """
    It finds the total distance of a route using a "calculated matrix".


    
    Args:
        route (List[int]): Route list containing city indices (from 0 to N-1).
        distance_matrix (np.ndarray): Distance matrix.
        
    Returns:
        float: Total length of the route (including return to the starting point).
    """

    # Convert List to array
    r = np.array(route)

    # Create a list of "next cities" by shifting the route one step at a time.
    # Example: route=[0, 1, 2] -> next_cities=[1, 2, 0]
    next_cities = np.roll(r, -1)

    # Perform vector summation on matrix 
    # distance_matrix[r, next_cities] -> retrieves the distances between route[i] and next_cities[i].
    total_dist = np.sum(distance_matrix[r, next_cities])

    return float(total_dist)