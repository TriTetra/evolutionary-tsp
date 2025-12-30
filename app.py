import streamlit as st
import pandas as pd
import time
import os
import json
import sys

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
generations = st.sidebar.slider("Nesil Sayısı (Generations)", 100, 2000, 500)
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

cities = read_tsp_file(file_path)

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
        with open("results/hall_of_fame.json", "r") as f:
            data = json.load(f)
            # Sadece seçili haritayı filtrele
            filtered = [d for d in data if d.get("dataset") == dataset_choice]
            # Mesafeye göre sırala
            filtered.sort(key=lambda x: x["final_distance"])
            
            df = pd.DataFrame(filtered)
            if not df.empty:
                # Sadece gerekli kolonları göster
                display_df = df[["run_name", "final_distance", "best_found_at_gen", "time_elapsed_sec"]]
                display_df.columns = ["Oyuncu", "Mesafe", "Nesil", "Süre"]
                leaderboard_placeholder.dataframe(display_df.head(10), hide_index=True)
            else:
                leaderboard_placeholder.info("Bu haritada henüz rekor yok.")
    else:
        leaderboard_placeholder.info("Liderlik tablosu henüz boş.")

# Sayfa açılışında tabloyu göster
load_and_show_leaderboard()

# --- OYUNU BAŞLAT ---
if st.sidebar.button("🚀 EVRİMİ BAŞLAT", type="primary"):
    
    # Konfigürasyon sözlüğü oluştur (Motor için)
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
            "mutation": "inversion", # Sabit tutuyoruz veya menüye ekleyebilirsin
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
        local_search_method=method_local
    )

    # İlerleme Çubuğu
    progress_bar = st.progress(0)
    
    # --- CANLI DÖNGÜ ---
    # Not: ga.run() tek seferde çalışır, canlı güncelleme için döngüyü burada manuel kuruyoruz
    # veya ga class'ını modifiye etmeden ara değerleri alamayız.
    # Şimdilik "sonuç odaklı" gösterim yapalım, sonra canlıya çeviririz.
    
    with st.spinner("Yapay zeka rotayı optimize ediyor..."):
        start_time = time.time()
        
        # Motor çalışıyor...
        best_route, best_distance, initial_dist, best_gen = ga.run(generations=generations, verbose=0)
        
        end_time = time.time()
        duration = end_time - start_time
        
        progress_bar.progress(100)

    # --- SONUÇLARI GÖSTER ---
    stats_placeholder.success(f"Bitti! Mesafe: **{best_distance:.2f}** (Süre: {duration:.2f}s)")
    
    # Haritayı Çiz
    route_cities = [cities[i] for i in best_route]
    route_cities.append(route_cities[0]) # Döngüyü kapat
    
    df_map = pd.DataFrame([{ 'lat': c.y, 'lon': c.x } for c in route_cities]) # X/Y kordinatlarını kullan
    
    # Streamlit scatter plot (basit çizim)
    st.line_chart(df_map, x='lon', y='lat')

    # Skoru Kaydet
    save_result(config, best_distance, best_route, duration, initial_dist, best_gen)
    
    st.balloons() # Konfeti patlat! 🎉
    
    # Tabloyu güncelle
    load_and_show_leaderboard()