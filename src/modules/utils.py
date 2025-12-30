import math
import numpy as np
from typing import List, Tuple

from .models import City


def read_tsp_file(filename:str) -> dict:

    """
    Reads a TSP file and extracts cities and edge weight type.

    Args:
        filename (str): .tsp file path.
        
    Returns:
        dict: {'cities': List[City], 'edge_weight_type': str}
    """

    cities = []
    edge_weight_type = "EUC_2D"

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

        # Catch file type (ATT or EUC_2D)?
        if line.startswith("EDGE_WEIGHT_TYPE"):
            parts = line.split(":")
            if len(parts) > 1:
                edge_weight_type = parts[1].strip()

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

    return {'cities': cities, 'edge_weight_type': edge_weight_type}


def compute_distance_matrix(cities: List[City], edge_weight_type: str = 'EUC_2D') -> np.ndarray:
    """
    Calculates NxN distance matrix based on edge_weight_type.
    
    Args:
        cities (List[City]): List of cities.
        edge_weight_type (str): 'EUC_2D' or 'ATT'.
        
    Returns:
        np.ndarray: NxN distance matrix.
    """
    n = len(cities)

    # converting the coords to the numpy array
    coords_list = []
    for c in cities:
        coords_list.append((c.x, c.y))

    coords_list = np.array(coords_list, dtype=np.float64)

    # Find the difference between all pairs using Broadcasting: (x1-x2, y1-y2)
    deltas = coords_list[:, np.newaxis, :] - coords_list[np.newaxis, :, :]

    if edge_weight_type == "ATT":
        # --- ATT (Pseudo-Euclidean) CALCULATION ---
        # Special formula according to TSPLIB standards.
        # rij = np.sqrt((deltas[:, :, 0]**2 + deltas[:, :, 1]**2) / 10.0)
        # tij = np.round(rij)

        # 1. Divide the sum of the squares by 10.
        sum_sq_div_10 = np.sum(deltas**2, axis=-1) / 10.0

        # 2. Take the square root and round up (ceil)
        dists = np.ceil(np.sqrt(sum_sq_div_10)).astype(int)

        # dists = np.ceil(rij).astype(int)
        # dists = np.ceil(np.sqrt(np.sum(deltas**2, axis=-1) / 10.0)).astype(int)

    else:
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