import random
import numpy as np
from typing import List, Tuple
import copy
from tqdm import tqdm

from .models import City 
from . import utils
from . import selection
from . import crossover
from . import mutation
from . import optimization

class GeneticAlgorithm:

    def __init__(
        self, 
        cities: List[City], 
        pop_size: int = 100, 
        mutation_rate: float = 0.01,
        elite_size: int = 2,
        selection_method: str = "tournament",
        crossover_method: str = "ordered",
        mutation_method: str = "inversion",
        local_search_method: str = "none",
        edge_weight_type: str = "EUC_2D"
    ):
        self.cities = cities
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size

        self.distance_matrix = utils.compute_distance_matrix(cities, edge_weight_type)
        
        self.selection_method = selection_method
        self.crossover_method = crossover_method
        self.mutation_method = mutation_method
        self.local_search_method = local_search_method
        
        # Tracking Variables
        self.population: List[List[int]] = []
        self.best_route: List[int] = []
        self.best_distance: float = float('inf')
        self.initial_distance: float = 0.0  # Best distance at the start
        self.best_generation: int = 0       # The generation that found the best.
        self.fitness_history: List[float] = []


    def initialize_population(self):
        self.population = []
        num_cities = len(self.cities)
        base_route = list(range(num_cities))
        for _ in range(self.pop_size):
            route = random.sample(base_route, num_cities)
            self.population.append(route)
            
        # İlk değerlendirme
        scores = self._evaluate_population()
        # Save initial state
        self.initial_distance = self.best_distance


    def _evaluate_population(self) -> List[float]:
        scores = []
        for route in self.population:
            dist = utils.calculate_route_distance(route, self.distance_matrix)
            scores.append(dist)
            
            if dist < self.best_distance:
                self.best_distance = dist
                self.best_route = list(route)
                
        return scores


    def _select_parents(self, scores: List[float]) -> List[List[int]]:
        """Wrapper to call the appropriate selection function."""
        num_parents = self.pop_size
        if self.selection_method == "tournament":
            return selection.tournament_selection(self.population, scores, num_parents)
        elif self.selection_method == "roulette":
            return selection.roulette_wheel_selection(self.population, scores, num_parents)
        elif self.selection_method == "rank":
            return selection.rank_based_selection(self.population, scores, num_parents)
        else:
            raise ValueError(f"Unknown selection method: {self.selection_method}")


    def _crossover_pairs(self, parent_pool: List[List[int]]) -> List[List[int]]:
        """Creates children using the selected crossover method."""
        children = []

        pop_with_scores = []
        for route in self.population:
             d = utils.calculate_route_distance(route, self.distance_matrix)
             pop_with_scores.append((d, route))

        pop_with_scores.sort(key=lambda x: x[0])
        
        # Elitizm: En iyileri koru
        for i in range(self.elite_size):
            children.append(pop_with_scores[i][1])

        # Fill in the rest
        i = 0
        while len(children) < self.pop_size:
            p1 = parent_pool[i % len(parent_pool)]
            p2 = parent_pool[(i + 1) % len(parent_pool)]

            if self.crossover_method == "ordered":
                c1, c2 = crossover.ordered_crossover(p1, p2)
            elif self.crossover_method == "cycle":
                c1, c2 = crossover.cycle_crossover(p1, p2)
            else:
                 c1, c2 = crossover.ordered_crossover(p1, p2)

            children.append(c1)
            if len(children) < self.pop_size:
                children.append(c2)

            i += 2

        return children


    def _mutate_population(self, children: List[List[int]]) -> List[List[int]]:
        """Applies mutation."""
        mutated_pop = []

        for idx, route in enumerate(children):
            # Elit bireylere dokunma
            if idx < self.elite_size:
                mutated_pop.append(route)
                continue

            if self.mutation_method == "swap":
                mutated_route = mutation.swap_mutation(list(route), self.mutation_rate)
            elif self.mutation_method == "insert":
                mutated_route = mutation.insert_mutation(list(route), self.mutation_rate)
            elif self.mutation_method == "inversion":
                mutated_route = mutation.inversion_mutation(list(route), self.mutation_rate)
            else:
                mutated_route = list(route)

            mutated_pop.append(mutated_route)

        return mutated_pop


    def run(self, generations: int = 100, verbose: int = 1, progress_callback=None, stop_threshold: int = None):
        """
        stop_threshold: (int) Eğer bu kadar nesil boyunca iyileşme olmazsa döngüyü kır.
        """
        if not self.population:
            self.initialize_population()
            
        iterator = range(generations)
        if verbose == 1:
            iterator = tqdm(iterator, desc="Evolving")
            
        # --- Stability Counter ---
        stability_counter = 0
        
        for gen in iterator:
            prev_best = self.best_distance
            
            # 1. Değerlendirme
            scores = self._evaluate_population()
            
            # --- İyileşme Kontrolü ---
            if self.best_distance < prev_best:
                self.best_generation = gen
                stability_counter = 0 # Sıfırla
            else:
                stability_counter += 1 # Artır
            
            # --- Erken Durdurma Kontrolü ---
            if stop_threshold and stability_counter >= stop_threshold:
                if verbose > 0:
                    print(f"\n✋ Stability Limit Reached ({stop_threshold} generations). Stopping Early!")
                if progress_callback:
                    progress_callback(1.0, gen, self.best_distance, "Kararlılık sınırına ulaşıldı. Erken durduruluyor.")
                break
            # -------------------------------

            self.fitness_history.append(self.best_distance)
            
            if verbose == 2 and gen % 10 == 0:
                print(f"Gen {gen}: Best = {self.best_distance:.2f}")
            
            # --- Callback ---
            if progress_callback:
                if gen % max(1, generations // 100) == 0:
                    progress_ratio = (gen + 1) / generations
                    progress_callback(progress_ratio, gen + 1, self.best_distance)

            # 2. Seçim
            parent_pool = self._select_parents(scores)
            # 3. Çaprazlama
            children = self._crossover_pairs(parent_pool)
            # 4. Mutasyon
            next_generation = self._mutate_population(children)
            # Güncelleme
            self.population = next_generation
            
        # 5. Hibrit Optimizasyon (Local Search)
        if self.local_search_method in ["2opt", "3opt"]:
            # Local search başladığını bildir
            if progress_callback:
                progress_callback(0.99, generations, self.best_distance, "Local Search (Optimize Ediliyor)...")

            if verbose > 0:
                print(f"\nApplying {self.local_search_method} optimization...")
            
            if self.local_search_method == "2opt":
                optimized_route = optimization.two_opt_optimization(self.best_route, self.distance_matrix)
            elif self.local_search_method == "3opt":
                optimized_route = optimization.three_opt_optimization(self.best_route, self.distance_matrix, max_iters=2000)
            else:
                optimized_route = self.best_route
                
            opt_dist = utils.calculate_route_distance(optimized_route, self.distance_matrix)
            
            if opt_dist < self.best_distance:
                self.best_distance = opt_dist
                self.best_route = optimized_route
                print(f"Local Search Improved: {self.best_distance:.2f}")

        return self.best_route, self.best_distance, self.initial_distance, self.best_generation