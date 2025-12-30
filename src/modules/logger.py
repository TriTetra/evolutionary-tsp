import json
import os
import datetime

# Bilinen en iyi sonuçlar (Referans için)
KNOWN_OPTIMALS = {
    "berlin52": 7542,
    "att48": 10628,
    "a280": 2579,
    "rat632": 12345, # Buraya rat632'nin gerçek optimalini bulup yazabilirsin
    "att532":27686
}

def save_result(config, best_distance, best_route, execution_time, initial_distance, best_generation):
    """
    Deney sonucunu, hesaplanan istatistiklerle birlikte kaydeder.
    """
    results_dir = "results"
    file_path = os.path.join(results_dir, "hall_of_fame.json")
    
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        
    history = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history = []

    # --- İSTATİSTİK HESAPLAMA ---
    
    # 1. Hangi veri seti?
    full_path = config.get("file_path", "")
    filename = os.path.basename(full_path) # örn: berlin52.tsp
    dataset_name = filename.replace(".tsp", "")
    
    # 2. Optimal Gap Hesaplama
    gap_percent = None
    if dataset_name in KNOWN_OPTIMALS:
        optimal = KNOWN_OPTIMALS[dataset_name]
        gap_percent = ((best_distance - optimal) / optimal) * 100
        gap_str = f"{gap_percent:.2f}%"
    else:
        gap_str = "Unknown"

    # 3. İyileşme Oranı (Improvement)
    improvement = initial_distance - best_distance
    improvement_percent = (improvement / initial_distance) * 100

    new_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "run_name": config.get("run_name", "Untitled Run"),
        
        # Veri Bilgisi
        "dataset": dataset_name,
        "num_cities": len(best_route),
        
        # Performans Metrikleri
        "final_distance": round(best_distance, 2),
        "initial_distance": round(initial_distance, 2),
        "improvement_pct": f"{improvement_percent:.2f}%",
        "time_elapsed_sec": round(execution_time, 2),
        
        # Kritik Analiz Verileri
        "best_found_at_gen": best_generation, # Hangi nesilde buldu?
        "total_generations": config["parameters"]["generations"],
        "gap_to_optimal": gap_str, # Optimalden ne kadar uzak?
        
        # Ayarlar
        "parameters": config["parameters"],
        "methods": config["methods"]
    }
    
    history.append(new_entry)
    history.sort(key=lambda x: x["final_distance"])
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)
        
    print(f"\n💾 [LOG] Sonuçlar kaydedildi.")
    print(f"📊 [ANALİZ] İyileşme: %{improvement_percent:.2f} | Optimal Farkı (Gap): {gap_str}")
    print(f"⏱️ [ZAMAN] En iyi çözüm {best_generation}. nesilde bulundu.")