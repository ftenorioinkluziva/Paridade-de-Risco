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
    
    selic = sgs.get(432, start="2024-06-01", timeout=90)
    ipca = sgs.get(13522, start="2024-06-01", timeout=90)
    
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
    
    ipca = sgs.get(433, start="2024-06-01", timeout=90)
    
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
    
    ibc = sgs.get(24363, start="2024-06-01", timeout=90)
    
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
    
    usd = sgs.get(3698, start="2024-06-01", timeout=90)
    
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
    
    igp = sgs.get(189, start="2024-06-01", timeout=90)
    
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


def grafico_estrutura_carteira():
    """Grafico 6: Estrutura da carteira - alocacao por ativo + risco por cenario."""
    print("  [6/6] Estrutura da carteira...", file=sys.stderr)

    # Dados da carteira (da nota Acompanhamento Junho 2026)
    ativos = [
        ("IFRM11", 37.50, "C4"),
        ("B5P211", 18.75, "C2+C3"),
        ("XFIX11", 14.00, "C1"),
        ("CDI", 12.50, "C2"),
        ("IB5M11", 7.00, "C1"),
        ("Dolar", 6.25, "C3"),
        ("BOVA11", 4.00, "C1"),
    ]

    cores_ativo = {
        "C1": "#00d4ff",   # azul
        "C2": "#ffaa33",   # amarelo/laranja
        "C3": "#ff4466",   # vermelho
        "C4": "#aa66ff",   # roxo
        "C2+C3": "#ff8844",# laranja-queimado
    }

    fig = plt.figure(figsize=(12, 5.5))
    fig.patch.set_facecolor(COR_FUNDO)

    # ========================
    # Painel 1: Donut de alocacao
    # ========================
    ax1 = fig.add_subplot(121)
    ax1.set_facecolor(COR_FUNDO)

    labels = [f"{a}\n{p:.1f}%" for a, p, _ in ativos]
    sizes = [p for _, p, _ in ativos]
    cores = [cores_ativo[c] for _, _, c in ativos]
    explode = [0.03] * len(ativos)
    # Destacar IFRM11 e B5P211 (maiores pesos)
    explode[0] = 0.08
    explode[1] = 0.05

    wedges, texts, autotexts = ax1.pie(
        sizes, explode=explode, labels=labels, colors=cores,
        autopct="", pctdistance=0.75,
        startangle=90, textprops={"color": COR_TEXTO, "fontsize": 8},
        wedgeprops={"linewidth": 0.5, "edgecolor": COR_FUNDO},
    )

    ax1.set_title("Alocacao por Ativo", color=COR_TEXTO,
                  fontsize=12, fontweight="bold", pad=15)

    # Legenda com cenários
    legenda_cores = {
        "C1 - Cresc+Desinf": cores_ativo["C1"],
        "C2 - Cresc+Infl": cores_ativo["C2"],
        "C3 - Estagflacao": cores_ativo["C3"],
        "C4 - Recessao": cores_ativo["C4"],
        "C2+C3 (B5P211)": cores_ativo["C2+C3"],
    }
    patches = [plt.Rectangle((0, 0), 1, 1, facecolor=c, edgecolor="none")
               for c in legenda_cores.values()]
    ax1.legend(patches, legenda_cores.keys(), loc="lower left",
               fontsize=7, facecolor=COR_FUNDO, edgecolor=COR_CINZA,
               framealpha=0.8, bbox_to_anchor=(0, -0.15))

    # ========================
    # Painel 2: Risco por cenario
    # ========================
    ax2 = fig.add_subplot(122)
    ax2.set_facecolor(COR_FUNDO)

    cenarios = ["C1\nAcoes/FIIs\nIPCA+", "C2\nCDI/B5P211", "C3\nDolar\nB5P211", "C4\nIFRM11\nPrefixado"]
    capital = [25.00, 25.00, 12.50, 37.50]
    vols = [9, 0, 18, 6]
    risco = [c * v / 100 for c, v in zip(capital, vols)]  # contribuicao de risco
    risco_pct = [r / sum(risco) * 100 if r > 0 else 0 for r in risco]
    cores_cenario = ["#00d4ff", "#ffaa33", "#ff4466", "#aa66ff"]

    # Barras de capital
    barras_capital = ax2.bar(
        np.arange(len(cenarios)) - 0.2, capital, width=0.35,
        color=[c + "55" for c in cores_cenario], edgecolor=cores_cenario,
        linewidth=1.5, alpha=0.7, label="Capital (%)"
    )

    # Barras de contribuicao de risco
    barras_risco = ax2.bar(
        np.arange(len(cenarios)) + 0.2, risco_pct, width=0.35,
        color=cores_cenario, edgecolor="white",
        linewidth=0.5, alpha=0.9, label="Risco (%)"
    )

    # Anotacoes
    for i in range(len(cenarios)):
        # Capital
        ax2.text(i - 0.2, capital[i] + 1, f"{capital[i]:.1f}%",
                 ha="center", fontsize=8, color=COR_TEXTO, fontweight="bold")
        # Risco
        if risco_pct[i] > 0:
            ax2.text(i + 0.2, risco_pct[i] + 1, f"{risco_pct[i]:.0f}%",
                     ha="center", fontsize=8, color=cores_cenario[i], fontweight="bold")
        else:
            ax2.text(i + 0.2, 1.5, "ancora",
                     ha="center", fontsize=7, color=COR_CINZA, style="italic")

    # Linha de referencia 33.3%
    ax2.axhline(y=33.33, color=COR_VERDE, linestyle="--", alpha=0.5, linewidth=1)
    ax2.text(3.3, 33.8, "33,3% (paridade)", color=COR_VERDE, fontsize=7, alpha=0.6)

    ax2.set_xticks(np.arange(len(cenarios)))
    ax2.set_xticklabels(cenarios, fontsize=8, color=COR_TEXTO)
    ax2.set_ylabel("%", color=COR_TEXTO, fontsize=10)
    ax2.set_title("Capital vs Risco por Cenário", color=COR_TEXTO,
                  fontsize=12, fontweight="bold", pad=15)
    ax2.legend(fontsize=7, facecolor=COR_FUNDO, edgecolor=COR_CINZA, loc="upper right")
    ax2.set_ylim(0, 50)
    ax2.spines["bottom"].set_color(COR_CINZA)
    ax2.spines["left"].set_color(COR_CINZA)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(axis="y", alpha=0.15, color=COR_CINZA)
    ax2.tick_params(colors=COR_TEXTO, labelsize=8)

    # Nota explicativa
    fig.text(0.5, 0.02,
             "Paridade de risco: C1 = C3 = C4 = 33,3% do risco total. "
             "C2 tem vol ~0% (ancora de liquidez).",
             ha="center", fontsize=8, color=COR_CINZA, style="italic")

    fig.tight_layout(rect=[0, 0.05, 1, 1])

    path = os.path.join(VAULT_PATH, "graf_estrutura_carteira.png")
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
    lines.append("## Estrutura da Carteira")
    lines.append("")
    lines.append("![[graf_estrutura_carteira.png]]")
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


def _safe_graf(func):
    """Wrapper que captura erros em graficos individuais."""
    try:
        return func()
    except Exception as e:
        print(f"  [!] Erro em {func.__name__}: {str(e)[:80]}", file=sys.stderr)
        return None


def main():
    print("Gerando dashboard BCB...\n", file=sys.stderr)
    
    os.makedirs(VAULT_PATH, exist_ok=True)
    
    funcoes = [
        grafico_selic_ipca,
        grafico_ipca_mensal,
        grafico_ibcbr,
        grafico_dolar,
        grafico_igpm,
        grafico_estrutura_carteira,
    ]
    
    caminhos = []
    for fn in funcoes:
        p = _safe_graf(fn)
        if p:
            caminhos.append(p)
    
    if not caminhos:
        print("[!] Nenhum grafico foi gerado!", file=sys.stderr)
        return
    
    print(f"\n[{len(caminhos)}/{len(funcoes)} graficos gerados]", file=sys.stderr)
    print("Gerando relatorio markdown...", file=sys.stderr)
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