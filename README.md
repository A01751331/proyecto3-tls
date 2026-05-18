# Proyecto 3 – MA2006B: Costo acumulado de múltiples handshakes TLS

**Curso:** MA2006B – Álgebra Moderna Aplicada a Seguridad y Criptografía  
**Institución:** Tecnológico de Monterrey  

---

## Pregunta técnica

¿Cómo se comporta la latencia acumulada al establecer múltiples conexiones TLS
consecutivas en escenarios realistas?

---

## Descripción del experimento

Se establecen N handshakes TLS consecutivos contra un servidor público real
(`www.google.com:443`), tratándolo como **caja negra**: solo se miden magnitudes
observables (latencia de conexión en ms). Se comparan TLS 1.2 y TLS 1.3 bajo los
mismos escenarios para analizar diferencias en costo acumulado.

### Variables

| Variable | Descripción |
|---|---|
| **Independiente** | Número de handshakes consecutivos N ∈ {10, 25, 50, 100, 200} |
| **Controlada** | Versión TLS (1.2 vs 1.3), host y puerto fijos, timeout = 10 s |
| **Dependiente** | Latencia por handshake (ms), latencia acumulada (ms) |
| **Variabilidad** | Cada escenario se repite 3 veces (REPETITIONS = 3) |

---

## Requisitos del entorno

- **OS:** Linux / macOS / Windows con WSL2
- **Python:** 3.10 o superior
- **Conexión a internet** (el experimento contacta `www.google.com:443`)

---

## Instalación de dependencias

```bash
pip install -r requirements.txt
```

---

## Ejecución del pipeline completo

### Paso 1 – Recolección de datos

```bash
python scripts/run_experiment.py
```

Genera: `data/results_raw.csv`

Tiempo estimado: ~5–15 min dependiendo de tu conexión de red.

### Paso 2 – Análisis y generación de figuras

```bash
python scripts/analyze.py
```

Genera en `results/`:
- `fig1_cumulative_latency.png`
- `fig2_avg_per_handshake.png`
- `fig3_latency_evolution.png`
- `table1_summary.csv`
- `table2_overhead.csv`

---

## Estructura del repositorio

```
proyecto3-tls/
├── README.md
├── requirements.txt
├── scripts/
│   ├── run_experiment.py   ← recolección de datos
│   └── analyze.py          ← análisis y visualización
├── data/
│   └── results_raw.csv     ← datos crudos generados
└── results/
    ├── fig1_cumulative_latency.png
    ├── fig2_avg_per_handshake.png
    ├── fig3_latency_evolution.png
    ├── table1_summary.csv
    └── table2_overhead.csv
```

---

## Control de variabilidad

Cada escenario N se ejecuta `REPETITIONS = 3` veces. Las figuras y tablas
reportan el promedio entre repeticiones. El parámetro `REPETITIONS` puede
modificarse en `run_experiment.py` para aumentar la robustez estadística.

La fuente principal de variabilidad es la latencia de red (jitter), que es
inherente al experimento de caja negra y se documenta mediante la desviación
estándar en `table1_summary.csv`.

---

## Uso de inteligencia artificial

Durante el desarrollo de este proyecto se utilizó IA (Claude, Anthropic) como
apoyo en la generación de código base para los scripts de recolección y análisis.
Todo el código fue revisado, ejecutado y validado manualmente por el equipo.
Los datos empíricos son originales y generados localmente.
