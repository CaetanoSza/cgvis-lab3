import csv
import math
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
PIB_PATH = SCRIPT_DIR / "pib2021.csv"
ICA_PATH = SCRIPT_DIR / "ica.csv"
OUTPUT_PATH = SCRIPT_DIR / "plot_pib_ica_boxplot.svg"

PIB_COL = "Contabilidade Social/Série 2002 em diante/PIB per capita 2021 (R$)"
ICA_COL = "IMERS/IQA/IQA 2022 (-)"

BINS = [
    (0, 20_000, "até R$ 20 mil"),
    (20_000, 35_000, "R$ 20-35 mil"),
    (35_000, 50_000, "R$ 35-50 mil"),
    (50_000, 75_000, "R$ 50-75 mil"),
    (75_000, 100_000, "R$ 75-100 mil"),
    (100_000, math.inf, "acima de R$ 100 mil"),
]


def br_number_to_float(value):
    value = str(value).strip()
    if not value or value == "-":
        return None
    return float(value.replace(".", "").replace(",", "."))


def read_csv_skip_title(path):
    with path.open(encoding="latin1", newline="") as file:
        lines = file.readlines()[1:]
    return list(csv.DictReader(lines))


def quantile(values, q):
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    lower = math.floor(pos)
    upper = math.ceil(pos)
    if lower == upper:
        return ordered[int(pos)]
    weight = pos - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def summarize(values):
    return {
        "min": min(values),
        "q1": quantile(values, 0.25),
        "median": quantile(values, 0.50),
        "q3": quantile(values, 0.75),
        "max": max(values),
        "n": len(values),
    }


def x_for(index, plot_left, plot_width):
    step = plot_width / len(BINS)
    return plot_left + step * index + step / 2


def y_for(value, plot_top, plot_height, y_min, y_max):
    return plot_top + (y_max - value) / (y_max - y_min) * plot_height


def svg_text(x, y, text, size=14, anchor="middle", weight="400", fill="#1f2933"):
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" '
        f'text-anchor="{anchor}" font-weight="{weight}" fill="{fill}">{text}</text>'
    )


def main():
    pib_rows = read_csv_skip_title(PIB_PATH)
    ica_rows = read_csv_skip_title(ICA_PATH)
    ica_by_ibge = {row["ibge"]: row for row in ica_rows}

    groups = {label: [] for _, _, label in BINS}
    for row in pib_rows:
        ica_row = ica_by_ibge.get(row["ibge"])
        if not ica_row:
            continue

        pib = br_number_to_float(row[PIB_COL])
        ica = br_number_to_float(ica_row[ICA_COL])
        if pib is None or ica is None:
            continue

        for low, high, label in BINS:
            if low <= pib < high:
                groups[label].append(ica)
                break

    summaries = [summarize(groups[label]) for _, _, label in BINS]
    total = sum(summary["n"] for summary in summaries)

    width = 1160
    height = 760
    plot_left = 105
    plot_right = 55
    plot_top = 120
    plot_bottom = 150
    plot_width = width - plot_left - plot_right
    plot_height = height - plot_top - plot_bottom
    y_min = 0
    y_max = 100
    box_width = 80

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        svg_text(width / 2, 46, "Distribuição do ICA 2022 por faixa de PIB per capita 2021", 24, weight="700"),
        svg_text(
            width / 2,
            76,
            f"{total} municípios do Rio Grande do Sul agrupados por nível de PIB per capita",
            15,
            fill="#52616b",
        ),
    ]

    for tick in range(0, 101, 20):
        y = y_for(tick, plot_top, plot_height, y_min, y_max)
        svg.append(f'<line x1="{plot_left}" y1="{y:.1f}" x2="{width - plot_right}" y2="{y:.1f}" stroke="#d9e2ec" stroke-width="1"/>')
        svg.append(svg_text(plot_left - 16, y + 5, str(tick), 13, anchor="end", fill="#52616b"))

    svg.append(f'<line x1="{plot_left}" y1="{plot_top}" x2="{plot_left}" y2="{plot_top + plot_height}" stroke="#334e68" stroke-width="1.4"/>')
    svg.append(f'<line x1="{plot_left}" y1="{plot_top + plot_height}" x2="{width - plot_right}" y2="{plot_top + plot_height}" stroke="#334e68" stroke-width="1.4"/>')

    for index, (_, _, label) in enumerate(BINS):
        summary = summaries[index]
        x = x_for(index, plot_left, plot_width)
        y_min_box = y_for(summary["min"], plot_top, plot_height, y_min, y_max)
        y_q1 = y_for(summary["q1"], plot_top, plot_height, y_min, y_max)
        y_median = y_for(summary["median"], plot_top, plot_height, y_min, y_max)
        y_q3 = y_for(summary["q3"], plot_top, plot_height, y_min, y_max)
        y_max_box = y_for(summary["max"], plot_top, plot_height, y_min, y_max)

        svg.append(f'<line x1="{x:.1f}" y1="{y_max_box:.1f}" x2="{x:.1f}" y2="{y_min_box:.1f}" stroke="#486581" stroke-width="2"/>')
        svg.append(f'<line x1="{x - 22:.1f}" y1="{y_max_box:.1f}" x2="{x + 22:.1f}" y2="{y_max_box:.1f}" stroke="#486581" stroke-width="2"/>')
        svg.append(f'<line x1="{x - 22:.1f}" y1="{y_min_box:.1f}" x2="{x + 22:.1f}" y2="{y_min_box:.1f}" stroke="#486581" stroke-width="2"/>')
        svg.append(
            f'<rect x="{x - box_width / 2:.1f}" y="{y_q3:.1f}" width="{box_width}" height="{y_q1 - y_q3:.1f}" '
            'fill="#2f80ed" fill-opacity="0.62" stroke="#1b4f9c" stroke-width="2"/>'
        )
        svg.append(f'<line x1="{x - box_width / 2:.1f}" y1="{y_median:.1f}" x2="{x + box_width / 2:.1f}" y2="{y_median:.1f}" stroke="#102a43" stroke-width="3"/>')

        first, second = label.split(" ", 1) if " " in label else (label, "")
        svg.append(svg_text(x, plot_top + plot_height + 34, first, 13, fill="#243b53"))
        svg.append(svg_text(x, plot_top + plot_height + 52, second, 13, fill="#243b53"))
        svg.append(svg_text(x, plot_top + plot_height + 78, f"n={summary['n']}", 12, fill="#627d98"))

    svg.append(svg_text(28, plot_top + plot_height / 2, "ICA 2022", 15, anchor="middle", weight="700", fill="#334e68").replace("<text ", '<text transform="rotate(-90 28 365)" ', 1))
    svg.append(svg_text(width / 2, height - 34, "Faixa de PIB per capita em 2021", 15, weight="700", fill="#334e68"))
    svg.append(
        svg_text(
            width / 2,
            height - 12,
            "Caixas mostram quartis e mediana; hastes mostram mínimo e máximo dentro de cada faixa.",
            12,
            fill="#627d98",
        )
    )
    svg.append("</svg>")

    OUTPUT_PATH.write_text("\n".join(svg), encoding="utf-8")
    print(f"Gráfico salvo em: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
