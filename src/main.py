import json
import os
import sys
import time

# ---------------------------------------------------------------------------
# MODÜLLERİ İÇERİ AKTARMA
# main.py ve modules klasörü aynı dizinde (src/) olduğu için
# doğrudan 'modules' paketi üzerinden import yapabiliriz.
# ---------------------------------------------------------------------------
try:
    from modules.utils import read_tsp_file
    from modules.ga_engine import GeneticAlgorithm
    from modules.logger import save_result
except ImportError as e:
    # Eğer yanlışlıkla proje kökünden "python src/main.py" diye çalıştırılırsa
    # Python bazen yolu bulamayabilir. Garantiye almak için:
    sys.path.append(os.path.dirname(__file__))
    from modules.utils import read_tsp_file
    from modules.ga_engine import GeneticAlgorithm
    from modules.logger import save_result

def get_project_root():
    """
    Projenin ana kök dizinini bulur.
    main.py 'src' içinde olduğu için, bir üst dizine ('..') çıkmamız gerekir.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Bir üst dizine çık (src'den proje köküne)
    return os.path.dirname(current_dir)


def load_config(root_dir):
    """
    config.json dosyasını proje kökünden yükler.
    """
    config_path = os.path.join(root_dir, "config.json")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"HATA: Ayar dosyası bulunamadı: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    print("=============================================")
    print("EVOLUTIONARY TSP SOLVER - BASLATILIYOR")
    print("=============================================")
    
    # 1. PROJE KÖKÜNÜ VE AYARLARI BULMA
    root_dir = get_project_root()
    print(f"[Sistem] Proje Kök Dizini: {root_dir}")

    try:
        config = load_config(root_dir)
        print(f"[Sistem] Ayarlar 'config.json' üzerinden yüklendi.")
    except Exception as e:
        print(f"[Hata] Konfigürasyon yüklenemedi: {e}")
        return

    # 2. VERİ SETİNİ YÜKLEME
    # Config'deki dosya yolunu proje köküne göre tam yola çevir
    relative_path = config.get("file_path", "data/berlin52.tsp")
    tsp_file = os.path.join(root_dir, relative_path)
    
    if not os.path.exists(tsp_file):
        print(f"[Hata] '{tsp_file}' dosyası bulunamadı!")
        print("   Lütfen 'config.json' içindeki 'file_path' ayarını kontrol edin.")
        return
        
    print(f"[Veri] TSP Dosyası Okunuyor: {relative_path}")

    tsp_data = read_tsp_file(tsp_file)
    cities = tsp_data['cities']
    weight_type = tsp_data['edge_weight_type']

    print(f"[Veri] Toplam {len(cities)} şehir başarıyla yüklendi.")
    print(f"[Veri] Hesaplama Tipi: {weight_type}")

    # 3. GENETİK ALGORİTMA MOTORUNU HAZIRLAMA
    params = config["parameters"]
    methods = config["methods"]
    
    print("\nALGORITMA PARAMETRELERI:")
    print(f"   Populasyon Buyuklugu : {params['pop_size']}")
    print(f"   Nesil Sayisi (Gen)   : {params['generations']}")
    print(f"   Mutasyon Orani       : {params['mutation_rate']}")
    print(f"   Seckinlik (Elitism)  : {params['elite_size']}")
    print("-" * 45)
    print(f"   Secim Yontemi        : {methods['selection']}")
    print(f"   Caprazlama           : {methods['crossover']}")
    print(f"   Mutasyon Yontemi     : {methods['mutation']}")
    print(f"   Yerel Arama (Hibrit) : {methods['local_search'].upper()}")
    print("-" * 45)

    # Motoru (Engine) Başlat
    ga = GeneticAlgorithm(
        cities=cities,
        pop_size=params["pop_size"],
        mutation_rate=params["mutation_rate"],
        elite_size=params["elite_size"],
        selection_method=methods["selection"],
        crossover_method=methods["crossover"],
        mutation_method=methods["mutation"],
        local_search_method=methods["local_search"],
        edge_weight_type=weight_type
    )


    # 4. EVRİMİ BAŞLATMA (RUN)
    print("\n🚀 Evrim Süreci Başlıyor...")
    start_time = time.time()

    stop_limit = params.get("stop_threshold", None)
    if stop_limit:
        print(f"🛑 Erken Durdurma Aktif: {stop_limit} nesil boyunca iyileşme olmazsa duracak.")

    # ARTIK 4 DEĞER DÖNÜYOR:
    best_route, best_distance, initial_dist, best_gen = ga.run(
        generations=params["generations"], 
        verbose=config["output"].get("verbose", 1),
        stop_threshold=stop_limit
    )
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # 5. SONUÇ RAPORLAMA
    print("\n=============================================")
    print("🏆 OPTİMİZASYON TAMAMLANDI")
    print("=============================================")
    print(f"⏱️  Toplam Süre      : {execution_time:.2f} saniye")
    print(f"📏 Başlangıç Mesafe : {initial_dist:.2f}")
    print(f"📏 En İyi Mesafe    : {best_distance:.2f}")
    print(f"📅 En İyi Nesil     : {best_gen}")
    print("=============================================")

    # SONUCU DETAYLI KAYDET
    # Parametre sayısına dikkat:
    save_result(config, best_distance, best_route, execution_time, initial_dist, best_gen)



if __name__ == "__main__":
    main()