#!/usr/bin/env python3
"""Generate real-world plots and CloudSim vs Real-world comparison plots."""
import os
import csv
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

OUT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(OUT, "..", "soka-a-5-main")

SERIES = {20: ("#2a78d6", "o", "k=20%"), 50: ("#eb6834", "s", "k=50%"), 100: ("#1baf7a", "^", "k=100%")}
SURFACE, INK, INK_MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"

METRICS = [
    ("makespan_s_mean", "Makespan", "detik (s)"),
    ("energy_kwh_mean", "Energi", "kWh"),
    ("cost_mean", "Biaya", "USD"),
    ("utilization_pct_mean", "Utilisasi", "%"),
    ("avg_response_s_mean", "Avg Response Time", "detik (s)"),
    ("vms_used_mean", "Jumlah VM Terpakai", "VM"),
    ("throughput_mean", "Throughput", "task/s"),
    ("di_mean", "Degree of Imbalance (semua VM)", ""),
    ("scheduling_ms_mean", "Waktu Penjadwalan", "ms"),
]

def load_grid(path):
    rows = defaultdict(dict)  # rows[k][tasks] = dict
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            k = int(float(r["k"]))
            t = int(float(r["tasks"]))
            rows[k][t] = {key: float(v) if v not in ("", None) else 0.0 for key, v in r.items()}
    return rows

def style_ax(ax, title, ylabel, xlabel="Jumlah Task"):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, color=INK, fontsize=12, fontweight="bold", pad=8)
    ax.set_xlabel(xlabel, color=INK_MUTED, fontsize=10)
    ax.set_ylabel(ylabel, color=INK_MUTED, fontsize=10)
    ax.tick_params(colors=INK_MUTED)
    ax.grid(True, color=GRID, linestyle="--", linewidth=0.8, alpha=0.9)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.legend(frameon=False, fontsize=9)

def plot_single(rows, metric, title, ylabel, out_path, dataset_label):
    fig, ax = plt.subplots(figsize=(8.5, 5.2), facecolor=SURFACE)
    for k in sorted(SERIES.keys()):
        if k not in rows:
            continue
        tasks = sorted(rows[k].keys())
        vals = [rows[k][t].get(metric, 0.0) for t in tasks]
        color, marker, label = SERIES[k]
        ax.plot(tasks, vals, color=color, marker=marker, label=label,
                linewidth=2.0, markersize=7, markerfacecolor=color, markeredgecolor="white", markeredgewidth=0.8)
    style_ax(ax, f"{title} — {dataset_label} (Real-World / Docker)", ylabel)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)

def plot_comparison(cs_rows, rw_rows, metric, title, ylabel, out_path, dataset_label):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.2), facecolor=SURFACE)
    for ax, rows, side in ((ax1, cs_rows, "CloudSim"), (ax2, rw_rows, "Real-World (Docker)")):
        for k in sorted(SERIES.keys()):
            if k not in rows:
                continue
            tasks = sorted(rows[k].keys())
            vals = [rows[k][t].get(metric, 0.0) for t in tasks]
            color, marker, label = SERIES[k]
            ax.plot(tasks, vals, color=color, marker=marker, label=label,
                    linewidth=2.0, markersize=7, markerfacecolor=color, markeredgecolor="white", markeredgewidth=0.8)
        style_ax(ax, f"{side}", ylabel)
    fig.suptitle(f"{title} — {dataset_label}\nCloudSim vs Real-World", color=INK, fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)

def plot_overlay_normalized(cs_rows, rw_rows, metric, title, ylabel, out_path, dataset_label):
    """Overlay after normalizing each series to its own k=100 at max tasks = 1.0, to compare shape.
    Actually better: show ratio RW/CS where tasks overlap, or dual axis.
    We'll do dual y-axis overlay for overlapping task counts.
    """
    # Find common tasks
    common = None
    for k in SERIES:
        if k in cs_rows and k in rw_rows:
            s = set(cs_rows[k]) & set(rw_rows[k])
            common = s if common is None else (common & s)
    if not common:
        return
    common = sorted(common)

    fig, ax1 = plt.subplots(figsize=(9.5, 5.4), facecolor=SURFACE)
    ax2 = ax1.twinx()
    lines = []
    for k in sorted(SERIES.keys()):
        if k not in cs_rows or k not in rw_rows:
            continue
        color, marker, label = SERIES[k]
        cs_vals = [cs_rows[k][t].get(metric, 0.0) for t in common]
        rw_vals = [rw_rows[k][t].get(metric, 0.0) for t in common]
        l1, = ax1.plot(common, cs_vals, color=color, marker=marker, linestyle="-",
                       linewidth=2.0, markersize=7, label=f"CS {label}")
        l2, = ax2.plot(common, rw_vals, color=color, marker=marker, linestyle="--",
                       linewidth=2.0, markersize=7, markerfacecolor="white", markeredgecolor=color,
                       markeredgewidth=1.5, label=f"RW {label}")
        lines.extend([l1, l2])
    ax1.set_facecolor(SURFACE)
    ax1.set_xlabel("Jumlah Task", color=INK_MUTED, fontsize=10)
    ax1.set_ylabel(f"CloudSim — {ylabel}", color=INK_MUTED, fontsize=10)
    ax2.set_ylabel(f"Real-World — {ylabel}", color=INK_MUTED, fontsize=10)
    ax1.tick_params(colors=INK_MUTED)
    ax2.tick_params(colors=INK_MUTED)
    ax1.grid(True, color=GRID, linestyle="--", linewidth=0.8, alpha=0.9)
    for spine in ax1.spines.values():
        spine.set_color(GRID)
    ax1.legend(lines, [l.get_label() for l in lines], frameon=False, fontsize=8, loc="upper left", ncol=2)
    ax1.set_title(f"{title} — {dataset_label}\nCloudSim (solid) vs Real-World (dashed, sumbu kanan)",
                  color=INK, fontsize=12, fontweight="bold", pad=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)

def write_table(rows, path, dataset_label, source_label):
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {dataset_label} — {source_label}\n\n")
        headers = ["tasks", "k"] + [m[0] for m in METRICS]
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
        for k in sorted(rows.keys()):
            for t in sorted(rows[k].keys()):
                r = rows[k][t]
                vals = [str(t), str(k)]
                for m, _, _ in METRICS:
                    v = r.get(m, 0.0)
                    if "pct" in m or m == "vms_used_mean":
                        vals.append(f"{v:.2f}")
                    elif "ms" in m:
                        vals.append(f"{v:.2f}")
                    elif "energy" in m:
                        vals.append(f"{v:.6f}")
                    elif "throughput" in m or "di" in m:
                        vals.append(f"{v:.4f}")
                    else:
                        vals.append(f"{v:.3f}")
                f.write("| " + " | ".join(vals) + " |\n")

def main():
    cs_gocj = load_grid(os.path.join(ROOT, "results/sessions/cloudsim_gocj_20261009_225810/grid_summary.csv"))
    cs_syn  = load_grid(os.path.join(ROOT, "results/sessions/cloudsim_synthetic_20261009_225854/grid_summary.csv"))
    rw_gocj = load_grid(os.path.join(ROOT, "realworld/results/sessions/all_20261028_023615/logs/gocj/grid_summary.csv"))
    rw_syn  = load_grid(os.path.join(ROOT, "realworld/results/sessions/all_20261028_023615/logs/synthetic/grid_summary.csv"))

    # Real-world only
    for metric, title, unit in METRICS:
        ylabel = f"{title} ({unit})" if unit else title
        plot_single(rw_gocj, metric, title, ylabel,
                    os.path.join(OUT, "realworld_only", f"gocj_{metric}.png"), "GoCJ")
        plot_single(rw_syn, metric, title, ylabel,
                    os.path.join(OUT, "realworld_only", f"synthetic_{metric}.png"), "Synthetic")

    # Side-by-side comparison
    for metric, title, unit in METRICS:
        ylabel = f"{title} ({unit})" if unit else title
        plot_comparison(cs_gocj, rw_gocj, metric, title, ylabel,
                        os.path.join(OUT, "comparison", f"gocj_cmp_{metric}.png"), "GoCJ")
        plot_comparison(cs_syn, rw_syn, metric, title, ylabel,
                        os.path.join(OUT, "comparison", f"synthetic_cmp_{metric}.png"), "Synthetic")

    # Overlay (dual axis) for overlapping points
    for metric, title, unit in METRICS:
        ylabel = f"{title} ({unit})" if unit else title
        plot_overlay_normalized(cs_gocj, rw_gocj, metric, title, ylabel,
                                os.path.join(OUT, "comparison", f"gocj_overlay_{metric}.png"), "GoCJ")
        plot_overlay_normalized(cs_syn, rw_syn, metric, title, ylabel,
                                os.path.join(OUT, "comparison", f"synthetic_overlay_{metric}.png"), "Synthetic")

    # Tables
    write_table(rw_gocj, os.path.join(OUT, "tables", "realworld_gocj.md"), "GoCJ", "Real-World (Docker)")
    write_table(rw_syn, os.path.join(OUT, "tables", "realworld_synthetic.md"), "Synthetic", "Real-World (Docker)")
    write_table(cs_gocj, os.path.join(OUT, "tables", "cloudsim_gocj.md"), "GoCJ", "CloudSim")
    write_table(cs_syn, os.path.join(OUT, "tables", "cloudsim_synthetic.md"), "Synthetic", "CloudSim")

    print("Done.")
    for root, _, files in os.walk(OUT):
        for fn in sorted(files):
            if fn.endswith((".png", ".md")):
                print(os.path.relpath(os.path.join(root, fn), OUT))

if __name__ == "__main__":
    main()
