# Analisis Grafik Real-World & Perbandingan CloudSim vs Real-World

Sumber data:
- **CloudSim GoCJ**: `results/sessions/cloudsim_gocj_20261009_225810/grid_summary.csv` (topologi 20 VM aktif)
- **CloudSim Synthetic**: `results/sessions/cloudsim_synthetic_20261009_225854/grid_summary.csv`
- **Real-World**: `realworld/results/sessions/all_20261028_023615/` (Docker, 20 container)

Catatan penting sebelum membaca grafik:
1. **Skala waktu berbeda.** CloudSim memakai waktu simulasi penuh (MI / MIPS) tanpa faktor `scale`. Real-world memakai faktor `scale` + `iters_per_mi` agar wall-clock di laptop tetap masuk akal. Karena itu nilai absolut makespan/energi/biaya/avg response CloudSim jauh lebih besar. Yang perlu dibandingkan adalah **pola/tren** (arah kurva, urutan k, bentuk pertumbuhan), bukan angka absolutnya.
2. Real-world GoCJ di sesi ini dimulai dari **200–1000** task (bukan 50). Synthetic **1000–10000** lengkap.
3. Real-world hanya **1 repetisi** per sel; CloudSim juga n=1 pada grid summary ini.

---

## A. Grafik Real-World saja (`realworld_only/`)

### 1. Makespan
Pada GoCJ maupun Synthetic, makespan **naik hampir linear** seiring jumlah task. Urutan konsisten: **k=20% paling lambat**, lalu k=50%, dan **k=100% paling cepat**. Artinya subset VM yang lebih besar (mendekati MCT) memberi completion time lebih baik. Pada Synthetic 10.000 task, selisih k=20 vs k=100 tetap terlihat jelas (~748 s vs ~548 s wall-clock).

### 2. Energi
Energi mengikuti makespan karena host tetap menyala selama simulasi/eksekusi. k=100% yang lebih cepat cenderung mengonsumsi energi sedikit lebih rendah. Pola ini sama di GoCJ dan Synthetic: kurva k=20 di atas, k=100 di bawah.

### 3. Biaya
Biaya juga sejalan dengan durasi (makespan). k lebih besar → selesai lebih cepat → biaya lebih rendah. Kenaikan biaya terhadap jumlah task hampir linear.

### 4. Utilisasi (%)
Utilisasi **sangat berbeda antar nilai k**:
- k=20% → hanya ~4 VM (V3) → utilisasi agregat rendah (~19–20%).
- k=50% → ~10 VM → utilisasi ~45–50%.
- k=100% → 20 VM → utilisasi tinggi (~90–97%).

Ini sesuai desain KPB: k kecil = konsolidasi ke VM tercepat; k besar = sebar ke semua VM.

### 5. Avg Response Time
Rata-rata waktu respons task naik seiring beban (jumlah task). k=100% umumnya memberi avg response lebih rendah daripada k=20%, karena antrian di tiap VM lebih pendek saat beban tersebar.

### 6. Jumlah VM Terpakai
Hampir konstan per k: k=20 → 4 VM, k=50 → 10 VM, k=100 → 20 VM. Grafik ini “datar” dan menegaskan bahwa KPB memilih subset berdasarkan persentase, bukan dinamis per task count.

### 7. Throughput (task/s)
Kebalikan makespan: k=100% paling tinggi, k=20% paling rendah. Throughput relatif stabil antar ukuran task (meski sedikit berfluktuasi di real-world karena noise wall-clock / CPU laptop).

### 8. Degree of Imbalance (DI, semua VM)
DI **turun tajam** saat k naik:
- k=20% → DI tinggi (~5), karena hanya 4 VM sibuk dan 16 VM idle.
- k=100% → DI rendah (~0.1–0.3), beban tersebar merata.

DI pada VM yang benar-benar terpakai (`di_used`) jauh lebih kecil; ketidakseimbangan besar di k kecil terutama karena banyak VM idle.

### 9. Waktu Penjadwalan (ms)
Waktu hitung mapping KPB sangat kecil (beberapa ms hingga puluhan ms) dibanding makespan. Naik perlahan dengan jumlah task, dan k=100 sedikit lebih mahal karena subset lebih besar, tetapi tetap dapat diabaikan untuk skala ini.

---

## B. Perbandingan CloudSim vs Real-World (`comparison/`)

Ada dua jenis file:
- `*_cmp_*.png` → **dua panel berdampingan** (kiri CloudSim, kanan Real-World)
- `*_overlay_*.png` → **satu grafik dual-axis** (CloudSim sumbu kiri solid, Real-World sumbu kanan dashed)

### Pola yang sama (validasi)
1. **Urutan k pada makespan, energi, biaya, throughput** sama di kedua platform: k=100 terbaik (makespan/energi/biaya rendah, throughput tinggi), k=20 terburuk.
2. **Utilisasi dan VM terpakai** sama-sama terikat ke k (≈19% / 4 VM, ≈48% / 10 VM, ≈95% / 20 VM).
3. **DI** sama-sama menurun drastis dari k=20 ke k=100.
4. **Bentuk kurva vs jumlah task** (naik linear untuk makespan/energi/biaya) konsisten.

Ini menunjukkan **keputusan penjadwalan KPB (mapping task→VM) yang sama** menghasilkan perilaku kualitatif yang sama saat dijalankan di simulator maupun di container Docker.

### Perbedaan yang terlihat
1. **Nilai absolut**: CloudSim jauh lebih besar karena tanpa `scale`. Real-world dikompres agar bisa diukur di laptop dalam hitungan menit–jam, bukan puluhan jam.
2. **Rasio nyata/prediksi**: di CloudSim mendekati 1.0; di real-world sering 2–3× (overhead container, penjadwalan OS, variasi P-core/E-core, noise I/O). Prediksi analitis di real-world under-estimate wall-clock, tetapi ranking antar-k tetap benar.
3. **Noise**: real-world sedikit lebih “bergelombang” (terutama scheduling time dan beberapa titik avg response) karena satu repetisi + lingkungan fisik; CloudSim deterministik.
4. **Titik data GoCJ**: CloudSim punya 50–1000; real-world sesi ini 200–1000. Synthetic keduanya 1000–10000.

### Makna untuk laporan
- Real-world **memvalidasi** temuan CloudSim: pada heterogenitas VM ini, **k=100% (setara MCT)** unggul di makespan, throughput, dan keseimbangan beban; k kecil hanya unggul jika tujuan utamanya konsolidasi ke sedikit VM (tapi di desain host yang tetap menyala, konsolidasi tidak menghemat energi secara signifikan).
- Perbedaan skala waktu tidak membatalkan perbandingan **relatif**; untuk klaim kuantitatif “X% lebih cepat”, pakai angka dalam platform yang sama, atau normalisasi (mis. selisih % antar k di dalam CloudSim, dan di dalam real-world secara terpisah).

---

## C. Ringkasan satu paragraf (siap tempel laporan)

Hasil real-world (Docker, 20 worker) pada dataset GoCJ dan Synthetic menunjukkan pola yang selaras dengan simulasi CloudSim: makespan, energi, dan biaya meningkat hampir linear terhadap jumlah task, dengan k=100% secara konsisten menghasilkan makespan terendah dan throughput tertinggi, sedangkan k=20% menghasilkan utilisasi rendah dan degree of imbalance tinggi karena hanya subset VM tercepat yang dipakai. Utilisasi dan jumlah VM terpakai ditentukan hampir sepenuhnya oleh parameter k, bukan oleh ukuran workload. Perbandingan berdampingan CloudSim–real-world mengonfirmasi bahwa mapping KPB yang sama menghasilkan tren metrik yang sama; perbedaan utama hanya pada skala absolut waktu (faktor scale di real-world) dan noise wall-clock, bukan pada ranking algoritma antar nilai k.
