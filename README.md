# 🧬 Evolutionary TSP Solver (ETS)
**Evolutionary TSP Solver**, NP-Zor (NP-Hard) sınıfındaki klasik kombinatoryal optimizasyon problemi olan **Gezgin Satıcı Problemi'ni (TSP)** çözmek için geliştirilmiş, yüksek performanslı ve modüler bir **Evrimsel Hesaplama (Evolutionary Computation)** kütüphanesidir.

Bu proje, sadece bir çözümleyici değil, aynı zamanda farklı genetik operatörlerin, hibrit yaklaşımların ve parametre setlerinin performansını analiz etmek için tasarlanmış bir **deney laboratuvarıdır**.

## Proje Hakkında
Bu çalışma, permütasyon tabanlı optimizasyon problemlerinde **Genetik Algoritmaların (GA) ve Yerel Arama (Local Search)** tekniklerinin etkinliğini araştırmayı amaçlar. Proje, saf genetik algoritmanın keşif (exploration) yeteneği ile yerel arama algoritmalarının sömürü (exploitation) yeteneğini birleştiren **Memetik Algoritmalar (Memetic Algorithms)** yapısını destekler.

Özellikle büyük ölçekli veri setlerinde (örn. att532, rat783) çözüm kalitesini artırmak için **2-Opt** ve **3-Opt** algoritmaları entegre edilmiştir.

### Temel Özellikler
- *[🧪]* **Modüler Araştırma Mimarisi**: Seçim, çaprazlama ve mutasyon operatörleri birbirinden bağımsız modüller halinde tasarlanmıştır (`Plug-and-Play`).
- *[⚡]* **Yüksek Performans**: Mesafe matrisleri ve popülasyon işlemleri `NumPy` kullanılarak vektörel hale getirilmiş, Python döngü maliyetleri minimize edilmiştir.
- *[🎮]* **Oyunlaştırılmış Arayüz (Gamified UI)**: `Streamlit` tabanlı web arayüzü ile parametrelerin anlık değiştirilmesi ve evrimin canlı izlenmesi sağlanır.
- *[📊]* **Deney Takibi (Experiment Tracking)**: Her çalıştırmanın sonucu (mesafe, süre, gap, parametreler) `JSON` formatında otomatik olarak kaydedilir ve analiz edilir.
 - *[🧠]* **Hibrit (Memetik) Yapı**: Genetik evrim sonrası `2-Opt` ve `3-Opt` ile "Local Search" iyileştirmesi.

### Kurulum
Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin:
```bash
# Repoyu klonlayın
git clone https://github.com/KULLANICI_ADINIZ/evolutionary-tsp-game.git
cd evolutionary-tsp-game

# Sanal ortam oluşturun (Önerilen)
python -m venv venv
# Windows için: .\venv\Scripts\activate
# Mac/Linux için: source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

## Kullanım
Projeyi üç farklı modda çalıştırabilirsiniz:
#### 1. Terminal Modu (Batch Processing)
Otomatik deneyler ve arka plan işlemleri için:
```bash
python src/main.py
```
*Ayarlar config.json dosyasından okunur.*
#### 2. Web Arayüzü (Interactive Mode)
Parametreleri canlı değiştirip yarışmak için:
```bash
streamlit run app.py
```
#### 3. Jupyter Notebook (Analysis Mode)
Sonuçları görselleştirmek ve grafik çizmek için:
```bash
jupyter notebook notebooks/demo.ipynb
```

## Algoritmik Detaylar ve Operatörler
Bu kütüphane aşağıdaki operatörleri desteklemektedir:
### 1. Seçim (Selection) Operatörleri
Ebeveynlerin gen havuzundan nasıl seçileceğini belirler.
- **Tournament Selection**: Rastgele seçilen $k$ birey arasından en iyisi seçilir. Seçim baskısı (Selection Pressure) ayarlanabilir.
- **Roulette Wheel**: Fitness değerine orantılı olasılıkla seçim yapar.
- **Rank Based**: Fitness değerine göre sıralama yapılarak seçim olasılıkları atanır.

### 2. Çaprazlama (Crossover) Operatörleri
- **Ordered Crossover (OX1)**: Sıra tabanlı problemlerde genetik dizilimi ve sırayı korumak için kullanılır [1].
- **Cycle Crossover (CX)**: Mutlak pozisyonları korumaya odaklanır [2].

### 3. Mutasyon (Mutation) Operatörleri
- Inversion Mutation: Bir alt diziyi ters çevirir. TSP için genellikle en etkili yöntemdir (2-Opt hareketine benzer).
- Swap Mutation: İki şehrin yerini değiştirir.
- Insert Mutation: Bir şehri alıp başka bir konuma ekler.

### 4. Yerel Arama (Local Search) - Hibritleşme
Genetik algoritma global optimuma yaklaştığında, sonucu iyileştirmek için deterministik algoritmalar devreye girer:
- **2-Opt**: Rotadaki iki kenarı (edge) silip çapraz bağlayarak kesişmeleri (crossing) çözer [3].
- **3-Opt**: Üç kenarı silip olası tüm yeniden bağlamaları dener. Daha yavaştır ancak daha iyi sonuç verir [4].


## 📂 Proje Yapısı

```text
evolutionary-tsp/
│
├── app.py                  # Streamlit Web Arayüzü (Game UI)
├── config.json             # Algoritma Konfigürasyonu
├── requirements.txt        # Kütüphane Bağımlılıkları
│
├── data/                   # TSP Veri Setleri (TSPLIB formatı)
│   ├── berlin52.tsp
│   └── att532.tsp
│
├── results/                # Deney Sonuçları (Loglar)
│   └── hall_of_fame.json
│
├── src/                    # Çekirdek Kaynak Kodlar
│   ├── main.py             # Terminal çalıştırıcısı
│   └── modules/            # Algoritma Modülleri
│       ├── ga_engine.py    # Genetik Algoritma Motoru
│       ├── models.py       # Veri Modelleri (City)
│       ├── selection.py    # Seçim Fonksiyonları
│       ├── crossover.py    # Çaprazlama Fonksiyonları
│       ├── mutation.py     # Mutasyon Fonksiyonları
│       ├── optimization.py # 2-Opt & 3-Opt (Local Search)
│       ├── utils.py        # Dosya okuma & Mesafe Matrisi
│       └── logger.py       # Sonuç Kayıt Sistemi
│
└── notebooks/              # Analiz Notebookları
    ├── demo.ipynb
    └── analysis.ipynb
```

## Referanslar
Projede kullanılan algoritmalar aşağıdaki akademik çalışmalara dayanmaktadır:
1. **[OX1]** Davis, L. (1985). *"Applying adaptive algorithms to epistatic domains." Proceedings of the International Joint Conference on Artificial Intelligence (IJCAI).*
2. **[CX]** Oliver, I. M., Smith, D. J., & Holland, J. R. (1987). *"A study of permutation crossover operators on the traveling salesman problem." Proceedings of the Second International Conference on Genetic Algorithms.*
3. **[2-Opt]** Croes, G. A. (1958). *"A method for solving traveling-salesman problems." Operations Research,* 6(6), 791-812.
4. **[3-Opt]** Lin, S. (1965). *"Computer solutions of the traveling salesman problem." Bell System Technical Journal,* 44(10), 2245-2269.
5. **[GA]** Holland, J. H. (1975). *Adaptation in Natural and Artificial Systems. University of Michigan Press.*
