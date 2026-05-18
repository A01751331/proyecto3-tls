"""
run_experiment.py
Proyecto 3 – MA2006B: Costo acumulado de múltiples handshakes TLS
Ejecuta N handshakes TLS consecutivos y guarda métricas en data/results_raw.csv
"""

import ssl
import socket
import time
import csv
import os
import sys
import statistics
from datetime import datetime

# ──────────────────────────────────────────────
# CONFIGURACIÓN DEL EXPERIMENTO
# ──────────────────────────────────────────────
HOST = "www.google.com"          # Servidor TLS público (caja negra)
PORT = 443
SCENARIOS = [10, 25, 50, 100, 200]  # Número de handshakes consecutivos a probar
REPETITIONS = 3                  # Veces que se repite cada escenario (control de variabilidad)
TLS_VERSIONS = {
    "TLS_1_2": ssl.TLSVersion.TLSv1_2,
    "TLS_1_3": ssl.TLSVersion.TLSv1_3,
}
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "results_raw.csv")
TIMEOUT = 10  # segundos por conexión


def single_handshake(host: str, port: int, tls_version: ssl.TLSVersion) -> float:
    """
    Establece UNA conexión TLS y devuelve la latencia del handshake en milisegundos.
    Trata al servidor como caja negra: solo mide tiempo observable.
    """
    ctx = ssl.create_default_context()   # usa los CA del sistema (compatible con WSL)
    ctx.minimum_version = tls_version
    ctx.maximum_version = tls_version

    start = time.perf_counter()
    with socket.create_connection((host, port), timeout=TIMEOUT) as raw_sock:
        with ctx.wrap_socket(raw_sock, server_hostname=host) as tls_sock:
            _ = tls_sock.version()   # fuerza que el handshake se complete
    end = time.perf_counter()

    return (end - start) * 1000  # ms


def run_scenario(host, port, tls_version_name, tls_version, n_handshakes, rep):
    """
    Ejecuta N handshakes consecutivos y registra métricas por handshake y acumuladas.
    Devuelve lista de filas para el CSV.
    """
    rows = []
    latencies = []
    cumulative = 0.0

    print(f"  [{tls_version_name}] N={n_handshakes:>3} | rep={rep} ", end="", flush=True)

    for i in range(1, n_handshakes + 1):
        try:
            latency = single_handshake(host, port, tls_version)
        except Exception as e:
            print(f"\n  ERROR en handshake {i}: {e}")
            latency = float("nan")

        latencies_so_far = [l for l in latencies + [latency] if not (isinstance(l, float) and l != l)]
        cumulative += latency if latency == latency else 0.0  # NaN-safe

        rows.append({
            "timestamp": datetime.utcnow().isoformat(),
            "tls_version": tls_version_name,
            "n_total": n_handshakes,
            "repetition": rep,
            "handshake_num": i,
            "latency_ms": round(latency, 3),
            "cumulative_ms": round(cumulative, 3),
            "avg_so_far_ms": round(
                statistics.mean(latencies_so_far) if latencies_so_far else float("nan"), 3
            ),
        })

        latencies.append(latency)
        print(".", end="", flush=True)

    print(f" ✓  total={cumulative:.1f}ms  avg={statistics.mean([l for l in latencies if l==l]):.1f}ms")
    return rows


def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    fieldnames = [
        "timestamp", "tls_version", "n_total", "repetition",
        "handshake_num", "latency_ms", "cumulative_ms", "avg_so_far_ms",
    ]

    print("=" * 60)
    print("  MA2006B – Proyecto 3: Costo acumulado de handshakes TLS")
    print(f"  Host: {HOST}:{PORT}")
    print(f"  Escenarios N: {SCENARIOS}")
    print(f"  Repeticiones por escenario: {REPETITIONS}")
    print(f"  Salida: {OUTPUT_FILE}")
    print("=" * 60)

    all_rows = []

    for tls_name, tls_ver in TLS_VERSIONS.items():
        print(f"\n── Versión: {tls_name} ──")
        for n in SCENARIOS:
            for rep in range(1, REPETITIONS + 1):
                rows = run_scenario(HOST, PORT, tls_name, tls_ver, n, rep)
                all_rows.extend(rows)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\n✅ Datos guardados: {OUTPUT_FILE}  ({len(all_rows)} filas)")


if __name__ == "__main__":
    main()
