import streamlit as st
import pandas as pd
import time
import os
import json
import sys
import matplotlib.pyplot as plt # Görselleştirme için ekledik

# Motoru import edebilmek için path ayarı
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.utils import read_tsp_file
from modules.ga_engine import GeneticAlgorithm
from modules.logger import save_result

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="TSP Evolution Game", layout="wide")

st.title("🧬 Evolutionary TSP: The Optimization Game")
st.markdown("En iyi parametreleri ayarla, algoritmayı çalıştır ve **Liderlik Tablosuna** adını yazdır!")

# --- SOL MENÜ (OYUNCU AYARLARI) ---
st.sidebar.header("🎮 Oyuncu Paneli")

nickname = st.sidebar.text_input("Nickname", value="Anonim Gezgin")
dataset_choice = st.sidebar.selectbox("Harita Seç (Level)", ["berlin52", "att48", "att532"])

st.sidebar.subheader("⚙️ Motor Ayarları")
pop_size = st.sidebar.slider("Popülasyon Büyüklüğü", 50, 500, 100)
generations = st.sidebar.slider("Nesil Sayısı (Generations)", 100, 5000, 500)
mutation_rate = st.sidebar.slider("Mutasyon Oranı", 0.0, 0.1, 0.01, step=0.001)
elite_size = st.sidebar.number_input("Elitizm (Korunacak En İyiler)", 0, 10, 2)

method_selection = st.sidebar.selectbox("Seçim Yöntemi", ["tournament", "roulette", "rank"])
method_crossover = st.sidebar.selectbox("Çaprazlama", ["ordered", "cycle"])
method_local = st.sidebar.selectbox("Yerel Arama (Bonus)", ["none", "2opt", "3opt"])

# --- DATA YÜKLEME ---
file_path = f"data/{dataset_choice}.tsp"
if not os.path.exists(file_path):
    st.error(f"Dosya bulunamadı: {file_path}")
    st.stop()

# GÜNCELLEME: Veriyi sözlük olarak alıyoruz
tsp_data = read_tsp_file(file_path)
cities = tsp_data['cities']
weight_type = tsp_data['edge_weight_type']

# Kullanıcıya bilgi ver
st.sidebar.info(f"📂 Veri: {dataset_choice} ({len(cities)} Şehir)\n📏 Tip: {weight_type}")

# --- ANA EKRAN ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🌍 Canlı Evrim Haritası")
    map_placeholder = st.empty()
    stats_placeholder = st.empty()

with col2:
    st.subheader("🏆 Hall of Fame (Top 10)")
    leaderboard_placeholder = st.empty()

# Liderlik Tablosunu Yükle ve Göster Fonksiyonu
def load_and_show_leaderboard():
    if os.path.exists("results/hall_of_fame.json"):
        try:
            with open("results/hall_of_fame.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Sadece seçili haritayı filtrele
            filtered = [d for d in data if d.get("dataset") == dataset_choice]
            # Mesafeye göre sırala
            filtered.sort(key=lambda x: x["final_distance"])
            
            if filtered:
                df = pd.DataFrame(filtered)
                # Sadece gerekli kolonları göster
                display_df = df[["run_name", "final_distance", "best_found_at_gen", "time_elapsed_sec"]]
                display_df.columns = ["Oyuncu", "Mesafe", "Nesil", "Süre"]
                leaderboard_placeholder.dataframe(display_df.head(10), hide_index=True)
            else:
                leaderboard_placeholder.info("Bu haritada henüz rekor yok.")
        except:
            leaderboard_placeholder.error("Liderlik tablosu okunamadı.")
    else:
        leaderboard_placeholder.info("Liderlik tablosu henüz boş.")

# Sayfa açılışında tabloyu göster
load_and_show_leaderboard()

# --- OYUNU BAŞLAT ---
if st.sidebar.button("🚀 EVRİMİ BAŞLAT", type="primary"):
    
    # Konfigürasyon sözlüğü
    config = {
        "run_name": nickname,
        "file_path": file_path,
        "parameters": {
            "pop_size": pop_size,
            "generations": generations,
            "mutation_rate": mutation_rate,
            "elite_size": elite_size
        },
        "methods": {
            "selection": method_selection,
            "crossover": method_crossover,
            "mutation": "inversion", 
            "local_search": method_local
        }
    }

    # Motoru Başlat
    ga = GeneticAlgorithm(
        cities=cities,
        pop_size=pop_size,
        mutation_rate=mutation_rate,
        elite_size=elite_size,
        selection_method=method_selection,
        crossover_method=method_crossover,
        mutation_method="inversion",
        local_search_method=method_local,
        edge_weight_type=weight_type 
    )

    # --- CANLI ARAYÜZ ELEMENTLERİ ---
    st.info("🧬 Evrimsel süreç başlatıldı...")
    
    # İlerleme Çubuğu
    progress_bar = st.progress(0.0)
    # Durum Metni (Anlık nesil ve mesafe)
    status_text = st.empty()
    # Anlık Metrik Kutuları
    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        gen_metric = st.empty()
    with metric_col2:
        dist_metric = st.empty()

    # --- CALLBACK FONKSİYONU ---
    def update_ui(progress, current_gen, current_dist, status_msg=None):
        # 0.0 ile 1.0 arasında tutalım (bazen taşabilir)
        prog_val = min(max(progress, 0.0), 1.0)
        progress_bar.progress(prog_val)
        
        if status_msg:
            status_text.info(f"⚡ Durum: {status_msg}")
        else:
            status_text.text(f"⚙️ İşleniyor... Nesil: {current_gen}/{generations}")
            
        # Metrikleri güncelle
        gen_metric.metric("Şu Anki Nesil", f"{current_gen}")
        dist_metric.metric("En İyi Mesafe", f"{current_dist:.2f}")

    # --- MOTORU ÇALIŞTIR ---
    start_time = time.time()
    
    # Callback fonksiyonumuzu gönderiyoruz
    best_route, best_distance, initial_dist, best_gen = ga.run(
        generations=generations, 
        verbose=0,
        progress_callback=update_ui
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    # İşlem bitince %100 yap
    progress_bar.progress(1.0)
    status_text.success("✅ Optimizasyon Tamamlandı!")

    # --- SONUÇLARI GÖSTER ---
    stats_placeholder.success(f"🏆 FİNAL: **{best_distance:.2f}** (Süre: {duration:.2f}s)")
    
    # Haritayı Çiz (Matplotlib)
    route_cities = [cities[i] for i in best_route]
    route_cities.append(route_cities[0]) 
    
    x_coords = [c.x for c in route_cities]
    y_coords = [c.y for c in route_cities]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x_coords, y_coords, 'b-', linewidth=1, alpha=0.7, label='Rota')
    ax.scatter(x_coords, y_coords, c='red', s=15, zorder=5) 
    ax.scatter(x_coords[0], y_coords[0], c='green', s=100, marker='*', label='Başlangıç')
    
    ax.set_title(f"En İyi Rota (Gen: {best_gen}) - {weight_type}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    # Eşit ölçeklendirme (Harita yamuk görünmesin)
    ax.set_aspect('equal', adjustable='box')

    map_placeholder.pyplot(fig)

    # Skoru Kaydet
    save_result(config, best_distance, best_route, duration, initial_dist, best_gen)
    
    st.balloons() 
    
    # Tabloyu güncelle
    load_and_show_leaderboard()