"""
analyze.py
Proyecto 3 – MA2006B: Costo acumulado de múltiples handshakes TLS
Lee data/results_raw.csv y genera tablas + figuras en results/
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

DATA_FILE   = os.path.join(os.path.dirname(__file__), "..", "data", "results_raw.csv")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")

COLORS = {
    "TLS_1_2": "#E85D24",
    "TLS_1_3": "#1D9E75",
}

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)
    df.dropna(subset=["latency_ms"], inplace=True)
    return df


def save_fig(name: str):
    path = os.path.join(RESULTS_DIR, name)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Figura guardada: {path}")


# ──────────────────────────────────────────────
# FIGURA 1 – Latencia acumulada vs N handshakes
# ──────────────────────────────────────────────

def fig_cumulative(df: pd.DataFrame):
    """
    Latencia acumulada al final de cada escenario N (promedio de repeticiones).
    Una línea por versión TLS.
    """
    summary = (
        df[df["handshake_num"] == df["n_total"]]   # solo la última fila de cada corrida
        .groupby(["tls_version", "n_total"])["cumulative_ms"]
        .mean()
        .reset_index()
        .rename(columns={"cumulative_ms": "mean_cumulative_ms"})
    )

    fig, ax = plt.subplots(figsize=(8, 4.5))

    for version, grp in summary.groupby("tls_version"):
        ax.plot(
            grp["n_total"], grp["mean_cumulative_ms"],
            marker="o", linewidth=2, color=COLORS[version], label=version.replace("_", " ")
        )

    ax.set_xlabel("Número de handshakes consecutivos (N)")
    ax.set_ylabel("Latencia acumulada promedio (ms)")
    ax.set_title("Fig. 1 – Latencia acumulada vs N handshakes TLS")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.tight_layout()
    save_fig("fig1_cumulative_latency.png")


# ──────────────────────────────────────────────
# FIGURA 2 – Latencia promedio por handshake
# ──────────────────────────────────────────────

def fig_avg_per_handshake(df: pd.DataFrame):
    """
    Latencia promedio por handshake individual para cada escenario N.
    Barras agrupadas por versión TLS.
    """
    summary = (
        df.groupby(["tls_version", "n_total"])["latency_ms"]
        .mean()
        .reset_index()
        .rename(columns={"latency_ms": "mean_latency_ms"})
    )

    versions = summary["tls_version"].unique()
    n_vals   = sorted(summary["n_total"].unique())
    x        = np.arange(len(n_vals))
    width    = 0.35

    fig, ax = plt.subplots(figsize=(8, 4.5))

    for i, version in enumerate(versions):
        vals = [
            summary.loc[
                (summary["tls_version"] == version) & (summary["n_total"] == n),
                "mean_latency_ms"
            ].values[0] if len(summary.loc[
                (summary["tls_version"] == version) & (summary["n_total"] == n)
            ]) > 0 else 0
            for n in n_vals
        ]
        offset = (i - len(versions) / 2 + 0.5) * width
        ax.bar(x + offset, vals, width, label=version.replace("_", " "),
               color=COLORS[version], alpha=0.85)

    ax.set_xlabel("Número de handshakes consecutivos (N)")
    ax.set_ylabel("Latencia promedio por handshake (ms)")
    ax.set_title("Fig. 2 – Latencia promedio por handshake individual")
    ax.set_xticks(x)
    ax.set_xticklabels(n_vals)
    ax.legend()
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    save_fig("fig2_avg_per_handshake.png")


# ──────────────────────────────────────────────
# FIGURA 3 – Evolución de latencia dentro de una corrida
# ──────────────────────────────────────────────

def fig_latency_evolution(df: pd.DataFrame):
    """
    Latencia de cada handshake #1..N para el escenario más grande.
    Muestra si hay warming-up o degradación progresiva.
    """
    n_max = df["n_total"].max()
    subset = df[df["n_total"] == n_max].copy()

    fig, ax = plt.subplots(figsize=(9, 4.5))

    for version, grp in subset.groupby("tls_version"):
        avg_by_num = grp.groupby("handshake_num")["latency_ms"].mean()
        ax.plot(avg_by_num.index, avg_by_num.values,
                linewidth=1.5, alpha=0.85, color=COLORS[version],
                label=version.replace("_", " "))

    ax.set_xlabel(f"Número de handshake dentro de la corrida (N={n_max})")
    ax.set_ylabel("Latencia (ms)")
    ax.set_title(f"Fig. 3 – Evolución de latencia durante {n_max} handshakes consecutivos")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    save_fig("fig3_latency_evolution.png")


# ──────────────────────────────────────────────
# TABLA 1 – Resumen estadístico
# ──────────────────────────────────────────────

def table_summary(df: pd.DataFrame):
    """
    Tabla con mean, std, min, max de latencia por versión y escenario N.
    Se guarda como CSV y se imprime en consola.
    """
    tbl = (
        df.groupby(["tls_version", "n_total"])["latency_ms"]
        .agg(
            mean_ms="mean",
            std_ms="std",
            min_ms="min",
            max_ms="max",
            n_obs="count",
        )
        .round(2)
        .reset_index()
    )

    path = os.path.join(RESULTS_DIR, "table1_summary.csv")
    tbl.to_csv(path, index=False)
    print(f"  Tabla guardada: {path}")
    print("\n── Tabla 1: Resumen estadístico ──")
    print(tbl.to_string(index=False))
    return tbl


# ──────────────────────────────────────────────
# TABLA 2 – Overhead acumulado relativo TLS 1.2 vs 1.3
# ──────────────────────────────────────────────

def table_overhead(df: pd.DataFrame):
    """
    Compara latencia acumulada media de TLS 1.2 vs 1.3 por escenario.
    """
    cumul = (
        df[df["handshake_num"] == df["n_total"]]
        .groupby(["tls_version", "n_total"])["cumulative_ms"]
        .mean()
        .unstack("tls_version")
        .reset_index()
    )
    if "TLS_1_2" in cumul.columns and "TLS_1_3" in cumul.columns:
        cumul["diff_ms"]    = (cumul["TLS_1_2"] - cumul["TLS_1_3"]).round(2)
        cumul["overhead_%"] = ((cumul["TLS_1_2"] - cumul["TLS_1_3"]) / cumul["TLS_1_3"] * 100).round(2)

    path = os.path.join(RESULTS_DIR, "table2_overhead.csv")
    cumul.to_csv(path, index=False)
    print(f"\n  Tabla guardada: {path}")
    print("\n── Tabla 2: Overhead TLS 1.2 vs TLS 1.3 ──")
    print(cumul.to_string(index=False))


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 60)
    print("  MA2006B – Proyecto 3: Análisis de resultados")
    print(f"  Leyendo: {DATA_FILE}")
    print("=" * 60)

    df = load_data()
    print(f"\n  Filas cargadas: {len(df)}")
    print(f"  Versiones TLS:  {df['tls_version'].unique().tolist()}")
    print(f"  Escenarios N:   {sorted(df['n_total'].unique().tolist())}")
    print(f"  Repeticiones:   {df['repetition'].nunique()}\n")

    print("Generando figuras...")
    fig_cumulative(df)
    fig_avg_per_handshake(df)
    fig_latency_evolution(df)

    print("\nGenerando tablas...")
    table_summary(df)
    table_overhead(df)

    print("\n✅ Análisis completo. Revisa la carpeta results/")


if __name__ == "__main__":
    main()
