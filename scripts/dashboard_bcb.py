#!/usr/bin/env python3
"""
Dashboard BCB - Paridade de Risco
==================================
Gera graficos dos principais indicadores economicos a partir dos dados
do SGS (Banco Central) e salva como PNG para inclusao no vault Obsidian.

Graficos gerados:
  1. Selic + IPCA 12m (juro real)
  2. IPCA mensal (barras)
  3. IBC-Br atividade economica
  4. Dolar Ptax
  5. IGP-M mensal
  6. Mapa de calor da carteira
"""

import sys
import os
import json
from datetime import datetime, timedelta
import matplotlib
matplotlib.use("Agg")  # sem display
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from bcb import sgs

# Config estilo
plt.style.use("dark_background")
COR_FUNDO = "#1a1a2e"
COR_TEXTO = "#e0e0e0"
COR_DESTAQUE = "#00d4ff"
COR_VERDE = "#00ff88"
COR_VERMELHO = "#ff4466"
COR_AMARELO = "#ffaa33"
COR_ROXO = "#aa66ff"
COR_CINZA = "#666666"

VAULT_PATH = "/opt/data/Paridade-de-Risco/99 - Anexos/graficos"


def config_axes(ax, titulo, ylabel=""):
    """Configura padrao de visual dos graficos."""
    ax.set_facecolor(COR_FUNDO)
    ax.set_title(titulo, color=COR_TEXTO, fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel(ylabel, color=COR_TEXTO, fontsize=10)
    ax.tick_params(colors=COR_TEXTO, labelsize=8)
    ax.spines["bottom"].set_color(COR_CINZA)
    ax.spines["left"].set_color(COR_CINZA)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, alpha=0.15, color=COR_CINZA)


def grafico_selic_ipca():
    """Grafico 1: Selic + IPCA 12m - juro real."""
    print("  [1/6] Selic + IPCA 12m...", file=sys.stderr)
    
    selic = sgs.get(432, start="2023-01-01", timeout=60)
    ipca = sgs.get(13522, start="2023-01-01", timeout=60)
    
    fig, ax1 = plt.subplots(figsize=(10, 4.5))
    fig.patch.set_facecolor(COR_FUNDO)
    config_axes(ax1, "Selic vs IPCA 12 meses", "% a.a.")
    
    ax1.plot(selic.index, selic.iloc[:, 0], color=COR_DESTAQUE, linewidth=2.5,
             label="Selic Meta", marker="o", markersize=3)
    ax1.plot(ipca.index, ipca.iloc[:, 0], color=COR_VERMELHO, linewidth=2,
             label="IPCA 12m", marker="s", markersize=3)
    
    # Juro real (Selic - IPCA) como area
    datas = selic.index
    selic_v = selic.iloc[:, 0].values
    ipca_v = ipca.reindex(datas, method="ffill").iloc[:, 0].values
    juro_real = selic_v - ipca_v
    ax1.fill_between(datas, 0, juro_real, where=juro_real > 0,
                     color=COR_VERDE, alpha=0.15, label="Juro real (+)")
    ax1.fill_between(datas, 0, juro_real, where=juro_real < 0,
                     color=COR_VERMELHO, alpha=0.15, label="Juro real (-)")
    
    # Teto da meta IPCA (4.5%)
    ax1.axhline(y=4.5, color=COR_AMARELO, linestyle="--", alpha=0.5, linewidth=1)
    ax1.text(selic.index[0], 4.55, "Teto meta (4,5%)", color=COR_AMARELO, fontsize=7, alpha=0.7)
    
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b/%y"))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax1.legend(loc="upper left", fontsize=8, facecolor=COR_FUNDO, edgecolor=COR_CINZA)
    
    fig.tight_layout()
    path = os.path.join(VAULT_PATH, "graf_selic_ipca.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=COR_FUNDO)
    plt.close(fig)
    return path


def grafico_ipca_mensal():
    """Grafico 2: IPCA mensal com limiares."""
    print("  [2/6] IPCA mensal...", file=sys.stderr)
    
    ipca = sgs.get(433, start="2024-01-01", timeout=60)
    
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor(COR_FUNDO)
    config_axes(ax, "IPCA Mensal (%)", "% ao mes")
    
    vals = ipca.iloc[:, 0].values
    cores = [COR_VERMELHO if v > 0.5 else COR_VERDE if v < 0.3 else COR_AMARELO for v in vals]
    
    ax.bar(ipca.index, vals, color=cores, width=20, alpha=0.85, edgecolor="none")
    
    # Linhas de referencia
    ax.axhline(y=0.5, color=COR_AMARELO, linestyle="--", alpha=0.4, linewidth=1)
    ax.text(ipca.index[0], 0.52, "0,50% (zona de alerta)", color=COR_AMARELO, fontsize=7, alpha=0.6)
    ax.axhline(y=0.3, color=COR_VERDE, linestyle="--", alpha=0.3, linewidth=1)
    ax.text(ipca.index[0], 0.32, "0,30% (zona confortavel)", color=COR_VERDE, fontsize=7, alpha=0.6)
    
    # Valor no topo de cada barra
    for i, v in enumerate(vals):
        cor_txt = COR_VERMELHO if v > 0.5 else COR_TEXTO
        ax.text(ipca.index[i], v + 0.02, f"{v:.2f}%", ha="center", fontsize=7,
                color=cor_txt, fontweight="bold")
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b/%y"))
    fig.tight_layout()
    
    path = os.path.join(VAULT_PATH, "graf_ipca_mensal.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=COR_FUNDO)
    plt.close(fig)
    return path


def grafico_ibcbr():
    """Grafico 3: IBC-Br atividade economica."""
    print("  [3/6] IBC-Br...", file=sys.stderr)
    
    ibc = sgs.get(24363, start="2023-01-01", timeout=60)
    
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor(COR_FUNDO)
    config_axes(ax, "IBC-Br (Atividade Economica)", "indice")
    
    ax.plot(ibc.index, ibc.iloc[:, 0], color=COR_ROXO, linewidth=2.5,
            marker="o", markersize=3)
    
    # Tendencia linear
    if len(ibc) > 5:
        x = np.arange(len(ibc))
        z = np.polyfit(x, ibc.iloc[:, 0].values, 1)
        p = np.poly1d(z)
        ax.plot(ibc.index, p(x), "--", color=COR_CINZA, alpha=0.5, linewidth=1,
                label=f"Tendencia ({z[0]:+.2f}/mes)")
        ax.legend(fontsize=8, facecolor=COR_FUNDO, edgecolor=COR_CINZA)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b/%y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    fig.tight_layout()
    
    path = os.path.join(VAULT_PATH, "graf_ibcbr.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=COR_FUNDO)
    plt.close(fig)
    return path


def grafico_dolar():
    """Grafico 4: Dolar Ptax."""
    print("  [4/6] Dolar...", file=sys.stderr)
    
    usd = sgs.get(3698, start="2024-01-01", timeout=60)
    
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor(COR_FUNDO)
    config_axes(ax, "Dolar Ptax (compra)", "R$")
    
    ax.plot(usd.index, usd.iloc[:, 0], color=COR_AMARELO, linewidth=2, marker=".", markersize=2)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b/%y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    fig.tight_layout()
    
    path = os.path.join(VAULT_PATH, "graf_dolar.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=COR_FUNDO)
    plt.close(fig)
    return path


def grafico_igpm():
    """Grafico 5: IGP-M mensal."""
    print("  [5/6] IGP-M mensal...", file=sys.stderr)
    
    igp = sgs.get(189, start="2024-01-01", timeout=60)
    
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor(COR_FUNDO)
    config_axes(ax, "IGP-M Mensal (%)", "% ao mes")
    
    vals = igp.iloc[:, 0].values
    cores = [COR_VERMELHO if v > 0.8 else COR_AMARELO if v > 0.5 else COR_VERDE for v in vals]
    
    ax.bar(igp.index, vals, color=cores, width=20, alpha=0.85)
    
    ax.axhline(y=0.5, color=COR_AMARELO, linestyle="--", alpha=0.4, linewidth=1)
    ax.axhline(y=1.0, color=COR_VERMELHO, linestyle="--", alpha=0.4, linewidth=1)
    ax.text(igp.index[0], 1.02, "1,00% (contagio severo)", color=COR_VERMELHO, fontsize=7, alpha=0.6)
    
    for i, v in enumerate(vals):
        if v > 1.0:
            ax.text(igp.index[i], v + 0.05, f"{v:.2f}%", ha="center", fontsize=7,
                    color=COR_VERMELHO, fontweight="bold")
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b/%y"))
    fig.tight_layout()
    
    path = os.path.join(VAULT_PATH, "graf_igpm.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=COR_FUNDO)
    plt.close(fig)
    return path


def grafico_mapa_calor():
    """Grafico 6: Mapa de calor da carteira por ativo x cenario."""
    print("  [6/6] Mapa de calor...", file=sys.stderr)
    
    # Dados da carteira (da nota Acompanhamento Junho 2026)
    ativos = ["IFRM11", "XFIX11", "B5P211", "CDI", "IB5M11", "Dolar", "BOVA11"]
    cenarios = ["C1\nCresc+Desinf", "C2\nCresc+Infl", "C3\nEstagflacao", "C4\nRecessao"]
    
    # Contribuicao de cada ativo em cada cenario (0=nenhuma, 1=parcial, 2=forte)
    exposicao = np.array([
        [0, 0, 0, 2],  # IFRM11 -> C4
        [2, 0, 0, 0],  # XFIX11 -> C1
        [1, 2, 2, 0],  # B5P211 -> C1+C2+C3
        [0, 2, 0, 0],  # CDI -> C2
        [2, 0, 0, 0],  # IB5M11 -> C1
        [0, 0, 2, 0],  # Dolar -> C3
        [2, 0, 0, 0],  # BOVA11 -> C1
    ])
    
    pesos = [37.5, 14.0, 18.75, 12.5, 7.0, 6.25, 4.0]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor(COR_FUNDO)
    
    im = ax.imshow(exposicao, cmap="RdYlGn", aspect="auto", vmin=0, vmax=2)
    
    ax.set_xticks(range(len(cenarios)))
    ax.set_xticklabels(cenarios, fontsize=9, color=COR_TEXTO)
    ax.set_yticks(range(len(ativos)))
    ax.set_yticklabels([f"{a} ({p:.0f}%)" for a, p in zip(ativos, pesos)],
                       fontsize=9, color=COR_TEXTO)
    
    # Valores nas celulas
    for i in range(len(ativos)):
        for j in range(len(cenarios)):
            v = exposicao[i, j]
            cor = "black" if v == 2 else "white"
            label = {0: "", 1: "~", 2: "●"}.get(v, "")
            ax.text(j, i, label, ha="center", va="center", fontsize=14, color=cor, fontweight="bold")
    
    ax.set_title("Exposicao por Ativo x Cenario", color=COR_TEXTO,
                 fontsize=13, fontweight="bold", pad=12)
    ax.spines[:].set_visible(False)
    
    fig.tight_layout()
    
    path = os.path.join(VAULT_PATH, "graf_mapa_calor.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=COR_FUNDO)
    plt.close(fig)
    return path


def gerar_relatorio_dashboard(caminhos):
    """Gera nota markdown no vault com os graficos."""
    hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    data_arq = datetime.now().strftime("%Y-%m-%d")
    
    lines = []
    lines.append("---")
    lines.append("tipo: dashboard")
    lines.append('categoria: "Macro"')
    lines.append("tags:")
    lines.append("  - dashboard")
    lines.append("  - graficos")
    lines.append("  - bcb")
    lines.append(f"data: {data_arq}")
    lines.append("status: gerado_automaticamente")
    lines.append("---")
    lines.append("")
    lines.append(f"# Dashboard BCB - {data_arq}")
    lines.append("")
    lines.append(f"> Gerado em {hoje}")
    lines.append("")
    lines.append("## Selic vs IPCA 12 meses")
    lines.append("")
    lines.append(f"![[graf_selic_ipca.png]]")
    lines.append("")
    lines.append("## IPCA Mensal")
    lines.append("")
    lines.append(f"![[graf_ipca_mensal.png]]")
    lines.append("")
    lines.append("## IBC-Br (Atividade Economica)")
    lines.append("")
    lines.append(f"![[graf_ibcbr.png]]")
    lines.append("")
    lines.append("## Dolar Ptax")
    lines.append("")
    lines.append(f"![[graf_dolar.png]]")
    lines.append("")
    lines.append("## IGP-M Mensal")
    lines.append("")
    lines.append(f"![[graf_igpm.png]]")
    lines.append("")
    lines.append("## Mapa de Calor da Carteira")
    lines.append("")
    lines.append(f"![[graf_mapa_calor.png]]")
    lines.append("")
    lines.append("---")
    lines.append(f"*Gerado em {hoje}*")
    
    path = os.path.join(
        "/opt/data/Paridade-de-Risco/01 - Notas Geradas",
        f"Dashboard BCB - {data_arq}.md"
    )
    
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    return path


def main():
    print("Gerando dashboard BCB...\n", file=sys.stderr)
    
    os.makedirs(VAULT_PATH, exist_ok=True)
    
    caminhos = []
    caminhos.append(grafico_selic_ipca())
    caminhos.append(grafico_ipca_mensal())
    caminhos.append(grafico_ibcbr())
    caminhos.append(grafico_dolar())
    caminhos.append(grafico_igpm())
    caminhos.append(grafico_mapa_calor())
    
    print("\nGerando relatorio markdown...", file=sys.stderr)
    relatorio = gerar_relatorio_dashboard(caminhos)
    
    print(f"\nDashboard salvo: {relatorio}", file=sys.stderr)
    print(f"Graficos em: {VAULT_PATH}/", file=sys.stderr)
    for p in caminhos:
        size = os.path.getsize(p) / 1024
        print(f"  {os.path.basename(p)}: {size:.0f} KB", file=sys.stderr)

    # Gateway: se chamado com --stdout, imprime caminhos
    if "--stdout" in sys.argv:
        print(relatorio)


if __name__ == "__main__":
    main()