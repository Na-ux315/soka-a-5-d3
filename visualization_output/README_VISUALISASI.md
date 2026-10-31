# Visualisasi Real-World & Perbandingan CloudSim

Folder ini **ditambahkan** (tidak ada di zip proyek asli). Berisi grafik yang digenerate dari `grid_summary.csv` CloudSim dan Real-World.

## Struktur (yang ditandai [BARU] = hasil generate)

```
visualization_output/                    [BARU]
├── README_VISUALISASI.md                [BARU] — file ini
├── ANALISIS.md                          [BARU] — analisis dalam bentuk kalimat
├── make_plots.py                        [BARU] — script generator
├── realworld_only/                      [BARU] — grafik real-world saja
│   ├── gocj_makespan_s_mean.png
│   ├── gocj_energy_kwh_mean.png
│   ├── gocj_cost_mean.png
│   ├── gocj_utilization_pct_mean.png
│   ├── gocj_avg_response_s_mean.png
│   ├── gocj_vms_used_mean.png
│   ├── gocj_throughput_mean.png
│   ├── gocj_di_mean.png
│   ├── gocj_scheduling_ms_mean.png
│   ├── synthetic_makespan_s_mean.png
│   ├── synthetic_energy_kwh_mean.png
│   ├── ... (9 metrik × 2 dataset = 18 file)
├── comparison/                          [BARU] — CloudSim vs Real-World
│   ├── gocj_cmp_*.png                   (panel kiri CS, kanan RW)
│   ├── synthetic_cmp_*.png
│   ├── gocj_overlay_*.png               (dual-axis: CS solid, RW dashed)
│   └── synthetic_overlay_*.png
└── tables/                              [BARU] — tabel angka sumber
    ├── realworld_gocj.md
    ├── realworld_synthetic.md
    ├── cloudsim_gocj.md
    └── cloudsim_synthetic.md
```

## Metrik (9)
1. Makespan  
2. Energi  
3. Biaya  
4. Utilisasi (%)  
5. Avg Response Time  
6. Jumlah VM Terpakai  
7. Throughput  
8. Degree of Imbalance  
9. Waktu Penjadwalan  

## Cara regenerate
```bash
# dari root artefak (setelah extract zip proyek)
python3 visualization_output/make_plots.py
```

## Legenda warna
- Biru lingkaran = k=20%
- Oranye kotak = k=50%
- Hijau segitiga = k=100%
