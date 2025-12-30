import numpy as np
from typing import List



def two_opt_optimization(route: List[int], distance_matrix: np.ndarray) -> List[int]:
    """
    Applies the 2-Opt Local Search algorithm.
    
    It iteratively removes two edges and reconnects them to reduce the total distance.
    This resolves "crossing" paths in the route.
    
    Complexity: O(N^2) per iteration.
    
    Args:
        route (List[int]): The initial route.
        distance_matrix (np.ndarray): Precomputed distance matrix.
        
    Returns:
        List[int]: The optimized route.
    """
    best_route = list(route)
    size = len(best_route)
    improved = True
    
    while improved:
        improved = False
        for i in range(1, size - 1):
            for j in range(i + 1, size):
                if j - i == 1: continue # Skip adjacent edges
                
                # Edges: (i-1, i) and (j, j+1)
                # Indices in the route list
                a, b = best_route[i - 1], best_route[i]
                c, d = best_route[j], best_route[(j + 1) % size]
                
                # Current distance of these two edges
                current_dist = distance_matrix[a][b] + distance_matrix[c][d]
                
                # New distance if we swap (reconnect a-c and b-d)
                new_dist = distance_matrix[a][c] + distance_matrix[b][d]
                
                if new_dist < current_dist:
                    # Apply 2-opt swap: Reverse the segment between i and j
                    best_route[i:j+1] = best_route[i:j+1][::-1]
                    improved = True
                    # Strategy: First Improvement (Return to start of loop immediately for speed)
                    # This is generally faster for TSP than Best Improvement.
                    break 
            if improved: break
        
    return best_route


def three_opt_optimization(route: List[int], distance_matrix: np.ndarray, max_iters: int = 1000) -> List[int]:
    """
    Applies the 3-Opt Local Search algorithm.
    
    It removes three edges and reconnects the three segments in the best possible way.
    It is more powerful than 2-Opt but significantly slower (O(N^3)).
    
    Engineering Note: Due to high complexity, 'max_iters' is used to prevent 
    excessive runtime on large datasets.
    
    Args:
        route (List[int]): Initial route.
        distance_matrix (np.ndarray): Distance matrix.
        max_iters (int): Maximum number of iterations (swaps) allowed.
    
    Returns:
        List[int]: Optimized route.
    """
    best_route = list(route)
    size = len(best_route)
    improved = True
    iteration = 0
    
    while improved and iteration < max_iters:
        improved = False
        iteration += 1
        
        # We need 3 cuts: i, j, k
        # Segments: [0...i-1], [i...j-1], [j...k-1], [k...N-1]
        for i in range(size - 4):
            for j in range(i + 2, size - 2):
                for k in range(j + 2, size):
                    # Edges to remove: (i-1, i), (j-1, j), (k-1, k)
                    # For simplicity in indexing, let's denote points:
                    # A=i-1, B=i, C=j-1, D=j, E=k-1, F=k
                    
                    A, B = best_route[i-1], best_route[i]
                    C, D = best_route[j-1], best_route[j]
                    E, F = best_route[k-1], best_route[k % size]
                    
                    # Current cost
                    d0 = distance_matrix[A][B] + distance_matrix[C][D] + distance_matrix[E][F]
                    
                    # There are 7 possible reconnections for 3-opt.
                    # We check moves that are NOT equivalent to 2-opt.
                    # (2-opt moves are handled by 2-opt function faster).
                    # Here we focus on pure 3-opt moves (reconnecting 3 segments).
                    
                    # Case 1: 2-opt like (A-C, B-D, E-F) - skipped
                    # Case 2: 2-opt like (A-B, C-E, D-F) - skipped
                    
                    # Let's check the specific 3-opt reconnections:
                    # 1. A-C, B-E, D-F (Reorder segments)
                    d1 = distance_matrix[A][C] + distance_matrix[B][E] + distance_matrix[D][F]
                    
                    # 2. A-D, E-B, C-F
                    d2 = distance_matrix[A][D] + distance_matrix[E][B] + distance_matrix[C][F]
                    
                    # 3. A-D, E-C, B-F
                    d3 = distance_matrix[A][D] + distance_matrix[E][C] + distance_matrix[B][F]
                    
                    # 4. A-E, D-B, C-F
                    d4 = distance_matrix[A][E] + distance_matrix[D][B] + distance_matrix[C][F]
                    
                    best_move = min(d0, d1, d2, d3, d4)
                    
                    if best_move < d0:
                        # Apply the best move
                        # Segments: S1=[i...j-1], S2=[j...k-1]
                        
                        seg1 = best_route[i:j]
                        seg2 = best_route[j:k]

                        if best_move == d1:
                            # A-C, B-E, D-F means: reverse S1, then S2, swap their order?
                            # Standard 3-opt move 1: reverse S1, then swap S1 and S2
                            # Reconstruct based on connections A(i-1) connects to C(j-1) -> S1 reversed
                            new_route = best_route[:i] + seg1[::-1] + seg2[::-1] + best_route[k:]
                            best_route = new_route
                            
                        elif best_move == d2:
                            # A-D(j), E(k-1)-B(i), C(j-1)-F(k)
                            # [..A] + [D...E] (S2) + [B...C] (S1) + [F..]
                            new_route = best_route[:i] + seg2 + seg1 + best_route[k:]
                            best_route = new_route
                            
                        elif best_move == d3:
                            # A-D(j), E(k-1)-C(j-1), B(i)-F(k)
                            # [..A] + [D...E] (S2) + [C...B] (S1 reversed) + [F..]
                            new_route = best_route[:i] + seg2 + seg1[::-1] + best_route[k:]
                            best_route = new_route
                        
                        elif best_move == d4:
                            # A-E(k-1), D(j)-B(i), C(j-1)-F(k)
                            # [..A] + [E...D] (S2 reversed) + [B...C] (S1) + [F..]
                            new_route = best_route[:i] + seg2[::-1] + seg1 + best_route[k:]
                            best_route = new_route
                            
                        improved = True
                        break # First improvement
                if improved: break
    
    return best_route