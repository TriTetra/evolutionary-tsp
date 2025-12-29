# Evolutionary TSP Solver

Bu proje, Gezgin Satıcı Problemi'ni (Traveling Salesperson Problem - TSP) çözmek için geliştirilmiş modüler, ölçeklenebilir ve araştırma odaklı bir Evrimsel Hesaplama (Evolutionary Computation) kütüphanesidir.

## 🎯 Proje Hakkında

Bu çalışma, klasik permütasyon tabanlı kombinatoryal optimizasyon problemlerini çözmek amacıyla geliştirilmiştir. Genetik Algoritma (GA) temelli olup, farklı seleksiyon, çaprazlama (crossover) ve mutasyon operatörlerinin performansını analiz etmeye olanak tanır. Ayrıca **2-Opt** ve **3-Opt** gibi yerel arama (local search) algoritmaları ile hibrit bir yapı sunar.

## 🚀 Özellikler

* **Modüler Mimari:** Operatörlerin kolayca değiştirilebildiği ve test edilebildiği yapı.
* **Optimize Edilmiş Hesaplama:** Mesafe matrisleri ve vektörel işlemler için `NumPy` kullanımı.
* **Çeşitli GA Operatörleri:**
    * *Selection:* Rank Based, Roulette Wheel
    * *Crossover:* Cycle Crossover (CX)
    * *Mutation:* Insert, Random Slide, Swap
* **Hibrit Yaklaşım:** Genetik Algoritma sonrası Local Search (2-Opt) entegrasyonu.

## 📂 Proje Yapısı

```text
evolutionary-tsp/
│
├── data/                   # TSP veri setleri (ör. berlin52.tsp)
├── src/                    # Kaynak kodlar
│   ├── models.py           # Veri yapıları (City, Route)
│   ├── selection.py        # Seçim algoritmaları
│   ├── crossover.py        # Çaprazlama operatörleri
│   ├── mutation.py         # Mutasyon operatörleri
│   ├── optimization.py     # Yerel arama (Local Search)
│   └── ga_engine.py        # Ana algoritma motoru
├── notebooks/              # Analiz ve görselleştirme notebookları
├── requirements.txt        # Bağımlılıklar
└── README.md               # Dokümantasyon