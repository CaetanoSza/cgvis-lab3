import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ----------------------------
# Arquivos
# ----------------------------
script_dir = Path(__file__).parent
pib_path = script_dir / "pib2021.csv"
ica_path = script_dir / "ica.csv"

# ----------------------------
# Leitura dos CSVs
# ----------------------------
pib = pd.read_csv(pib_path, encoding="latin1", header=1)
ica = pd.read_csv(ica_path, encoding="latin1", header=1)

# Nomes das colunas usadas
pib_col = "Contabilidade Social/Série 2002 em diante/PIB per capita 2021 (R$)"
ica_col = "IMERS/IQA/IQA 2022 (-)"

# ----------------------------
# Função para converter número BR para float
# Ex.: "45.123,67" -> 45123.67
# ----------------------------
def br_number_to_float(value):
    if pd.isna(value):
        return np.nan
    value = str(value).strip()
    if value in {"", "-"}:
        return np.nan
    return float(value.replace(".", "").replace(",", "."))

# ----------------------------
# Preparação dos dados
# ----------------------------
pib_plot = pib[["Município", "ibge", pib_col]].copy()
ica_plot = ica[["ibge", ica_col]].copy()

pib_plot["PIB per capita 2021"] = pib_plot[pib_col].apply(br_number_to_float)
ica_plot["ICA 2022"] = ica_plot[ica_col].apply(br_number_to_float)

df = pib_plot[["Município", "ibge", "PIB per capita 2021"]].merge(
    ica_plot[["ibge", "ICA 2022"]],
    on="ibge",
    how="inner"
).dropna()

# ----------------------------
# Estatísticas
# ----------------------------
n = len(df)
corr = df["PIB per capita 2021"].corr(df["ICA 2022"])

# Ajuste linear sobre log10(x), já que o eixo X é log
x = df["PIB per capita 2021"].to_numpy()
y = df["ICA 2022"].to_numpy()

x_log = np.log10(x)
coef = np.polyfit(x_log, y, 1)
trend = np.poly1d(coef)

# ----------------------------
# Gráfico
# ----------------------------
fig, ax = plt.subplots(figsize=(11, 7))

# Pontos
ax.scatter(
    df["PIB per capita 2021"],
    df["ICA 2022"],
    alpha=0.45,
    s=26
)

# Linha de tendência
x_line = np.geomspace(df["PIB per capita 2021"].min(), df["PIB per capita 2021"].max(), 300)
y_line = trend(np.log10(x_line))
ax.plot(x_line, y_line, linewidth=2)

# Escala log base 10 no eixo X
ax.set_xscale("log")

# Ticks explícitos
xticks = [10000, 20000, 50000, 100000, 200000, 500000]
xtick_labels = ["R$ 10 mil", "R$ 20 mil", "R$ 50 mil", "R$ 100 mil", "R$ 200 mil", "R$ 500 mil"]
ax.set_xticks(xticks)
ax.set_xticklabels(xtick_labels)

# Limites do eixo X
xmin = min(df["PIB per capita 2021"].min(), 10000)
xmax = max(df["PIB per capita 2021"].max(), 500000)
ax.set_xlim(xmin * 0.9, xmax * 1.05)

# Título e subtítulo
fig.suptitle("Relação entre PIB per capita de 2021 e ICA de 2022", fontsize=16, y=0.97)
ax.set_title(
    f"{n} municípios | Correlação de Pearson: {corr:.3f} | Eixo X em escala logarítmica (base 10)",
    fontsize=11,
    pad=10
)

# Rótulos dos eixos
ax.set_xlabel("PIB per capita em 2021")
ax.set_ylabel("ICA em 2022")

# Grade
ax.grid(True, alpha=0.25)

# Ajuste de layout
plt.tight_layout(rect=[0, 0, 1, 0.93])

# Salvar
output_path = script_dir / "plot_pib_ica_scatterplot.png"
plt.savefig(output_path, dpi=220, bbox_inches="tight")

# Mostrar
plt.show()

print(f"Gráfico salvo em: {output_path}")
