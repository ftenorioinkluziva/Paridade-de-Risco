#!/usr/bin/env python3
"""
Simulacao Longa - Paridade de Risco (2021-2026)
================================================
Performance historica real da carteira em paridade de risco.
Usa API Blackbox (precos historicos) + CDI do proprio dataset.
"""
import sys, json, os, statistics
from datetime import datetime
import urllib.request

API = "https://paridaderisco.blackboxinovacao.com.br/api/assets/prices"
VAULT = "/opt/data/Paridade-de-Risco/01 - Notas Geradas"

PORTFOLIO = [
    ("IFRM11", "FIXA11.SA", 0.375, "Prefixado"),
    ("B5P211", "B5P211.SA", 0.1875, "IMAB5"),
    ("XFIX11", "XFIX11.SA", 0.14, "FIIs"),
    ("CDI", "CDI_MENSAL", 0.125, "CDI"),
    ("IB5M11", "IB5M11.SA", 0.07, "IMAB5+"),
    ("DOLAR", "USDBRL=X", 0.0625, "Dolar"),
    ("BOVA11", "BOVA11.SA", 0.04, "Ibovespa"),
]


def get(ticker, start="2021-01-01", end="2026-06-22"):
    url = f"{API}?ticker={ticker}&from={start}&to={end}"
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode())


def calc_monthly_returns(data, is_cdi=False):
    """Calcula retorno mensal de cada ativo."""
    meses = {}
    for r in data:
        m = r["priceDate"][:7]
        if m not in meses:
            meses[m] = float(r["price"])

    ord_m = sorted(meses.keys())
    returns = {}
    for i in range(1, len(ord_m)):
        if is_cdi:
            # CDI_MENSAL: valor ja e o percentual do mes
            returns[ord_m[i]] = meses[ord_m[i]] / 100
        else:
            p_ant, p_at = meses[ord_m[i - 1]], meses[ord_m[i]]
            if p_ant > 0:
                returns[ord_m[i]] = (p_at / p_ant) - 1
    return returns, meses


def main():
    print("=== Simulacao Longa: 2021-2026 ===\n", file=sys.stderr)

    # Buscar dados
    all_returns = {}
    print("Baixando historico...", file=sys.stderr)
    for key, ticker, peso, nome in PORTFOLIO:
        print(f"  {key:8s} ({ticker})...", file=sys.stderr)
        data = get(ticker)
        ret, _ = calc_monthly_returns(data, is_cdi=(key == "CDI"))
        all_returns[key] = {"ret": ret, "peso": peso, "nome": nome}
        print(f"    {len(ret)} meses", file=sys.stderr)

    # Meses em comum
    meses_set = set()
    for v in all_returns.values():
        meses_set.update(v["ret"].keys())
    meses = sorted(m for m in meses_set if m >= "2021-01" and m <= "2026-06")

    # Simular carteira mes a mes
    port_val = [1000.0]
    cdi_val = [1000.0]
    bova_val = [1000.0]

    print(f"\nSimulando {len(meses)} meses...", file=sys.stderr)
    for i in range(1, len(meses)):
        mes = meses[i]

        # Portfolio
        rp = sum(v["peso"] * v["ret"].get(mes, 0) for v in all_returns.values())
        port_val.append(port_val[-1] * (1 + rp))

        # CDI
        r_cdi = all_returns["CDI"]["ret"].get(mes, 0)
        cdi_val.append(cdi_val[-1] * (1 + r_cdi))

        # BOVA11
        r_bova = all_returns["BOVA11"]["ret"].get(mes, 0)
        bova_val.append(bova_val[-1] * (1 + r_bova))

    # Metricas agregadas
    ret_total = (port_val[-1] / 1000 - 1) * 100
    ret_cdi = (cdi_val[-1] / 1000 - 1) * 100
    ret_bova = (bova_val[-1] / 1000 - 1) * 100

    n_meses = len(meses) - 1
    anos = n_meses / 12

    rets_m = [(port_val[i] / port_val[i - 1] - 1) for i in range(1, len(port_val))]
    vol_m = statistics.stdev(rets_m) if rets_m else 0
    vol_a = vol_m * (12 ** 0.5) * 100
    ret_a = ((port_val[-1] / 1000) ** (1 / anos) - 1) * 100 if anos > 0 else 0

    # Drawdown
    peak = port_val[0]
    max_dd = 0
    for v in port_val:
        if v > peak:
            peak = v
        dd = (v - peak) / peak * 100
        if dd < max_dd:
            max_dd = dd

    # Sharpe
    excess = [(port_val[i] / port_val[i - 1] - 1) - (cdi_val[i] / cdi_val[i - 1] - 1)
              for i in range(1, len(port_val))]
    sharpe = (statistics.mean(excess) / statistics.stdev(excess) * (12 ** 0.5)
              if excess and statistics.stdev(excess) > 0 else 0)

    # Retornos anuais
    anos_calc = {}
    for a in range(2021, 2027):
        m_ano = [m for m in meses if m.startswith(str(a))]
        if len(m_ano) < 2:
            continue
        i0 = meses.index(m_ano[0])
        i1 = meses.index(m_ano[-1])
        ret_ano = (port_val[i1] / port_val[i0] - 1) * 100
        cdi_ano = (cdi_val[i1] / cdi_val[i0] - 1) * 100
        bova_ano = (bova_val[i1] / bova_val[i0] - 1) * 100
        anos_calc[a] = (ret_ano, cdi_ano, bova_ano)

    # Relatorio
    hoje = datetime.now().strftime("%Y-%m-%d")
    L = []
    L.append("---")
    L.append("tipo: simulacao")
    L.append('categoria: "Performance"')
    L.append("tags:")
    L.append("  - simulacao")
    L.append("  - benchmark")
    L.append("  - longa")
    L.append("  - 5-anos")
    L.append(f"data: {hoje}")
    L.append("status: gerado_automaticamente")
    L.append("---")
    L.append("")
    L.append("# Simulacao 2021-2026 - Paridade de Risco")
    L.append("")
    L.append("> Dados reais via API Blackbox")
    L.append("")
    L.append("## Performance Acumulada")
    L.append("")
    L.append(f"| Periodo | Carteira RP | CDI | BOVA11 |")
    L.append(f"|--------|:----------:|:---:|:------:|")
    L.append(f"| **{meses[0]} a {meses[-1]} ({n_meses} meses)** | **{ret_total:+.2f}%** | {ret_cdi:+.2f}% | {ret_bova:+.2f}% |")
    L.append(f"| **Retorno Anualizado** | **{ret_a:.2f}%** | — | — |")
    L.append(f"| **Volatilidade (anual)** | **{vol_a:.2f}%** | ~0% | — |")
    L.append(f"| **Sharpe** | **{sharpe:.2f}** | — | — |")
    L.append(f"| **Max Drawdown** | **{max_dd:.2f}%** | 0% | — |")
    L.append("")

    if anos_calc:
        L.append("## Retornos Anuais")
        L.append("")
        L.append("| Ano | Carteira RP | CDI | BOVA11 |")
        L.append("|:---:|:----------:|:---:|:------:|")
        for a in sorted(anos_calc.keys()):
            rp, cdi, bova = anos_calc[a]
            L.append(f"| **{a}** | {rp:+.2f}% | {cdi:+.2f}% | {bova:+.2f}% |")
        L.append("")

    # Tabela de contribuicao
    L.append("## Contribuicao por Ativo (periodo total)")
    L.append("")
    L.append("| Ativo | Peso | Retorno Acum | Contribuicao |")
    L.append("|------|:---:|:-----------:|:-----------:|")
    for key, ticker, peso, nome in PORTFOLIO:
        rr = [all_returns[key]["ret"].get(m, 0) for m in meses[1:]]
        if rr:
            ret_acum = (1 + sum(rr) / len(rr)) ** len(rr) - 1
        else:
            ret_acum = 0
        contrib = peso * ret_acum * 100
        L.append(f"| {nome} | {peso*100:.1f}% | {ret_acum*100:+.2f}% | {contrib:+.2f}% |")
    L.append("")

    # Evolucao
    L.append("## Evolucao")
    L.append("")
    L.append("| Data | Carteira | CDI | BOVA11 |")
    L.append("|:---:|:--------:|:---:|:-----:|")

    # Amostrar a cada 6 meses para nao ficar enorme
    step = max(1, len(meses) // 12)
    for i in range(0, len(meses), step):
        L.append(f"| {meses[i]} | {port_val[i]:.1f} | {cdi_val[i]:.1f} | {bova_val[i]:.1f} |")
    # Ultimo
    L.append(f"| {meses[-1]} | {port_val[-1]:.1f} | {cdi_val[-1]:.1f} | {bova_val[-1]:.1f} |")
    L.append("")

    L.append("---")
    L.append(f"*Pesos fixos da paridade de risco | Fonte: API Blackbox*")

    fname = f"{VAULT}/Simulacao Longa 2021-2026 - {hoje}.md"
    with open(fname, "w") as f:
        f.write("\n".join(L))

    # Print summary
    print(f"\n{'='*50}", file=sys.stderr)
    print(f"RESULTADOS: {meses[0]} a {meses[-1]} ({n_meses} meses)", file=sys.stderr)
    print(f"{'='*50}", file=sys.stderr)
    print(f"  Carteira RP: {ret_total:+.2f}%  ({ret_a:.2f}% a.a.)", file=sys.stderr)
    print(f"  CDI:         {ret_cdi:+.2f}%", file=sys.stderr)
    print(f"  BOVA11:      {ret_bova:+.2f}%", file=sys.stderr)
    print(f"  Vol:         {vol_a:.2f}% a.a.", file=sys.stderr)
    print(f"  Sharpe:      {sharpe:.2f}", file=sys.stderr)
    print(f"  Max DD:      {max_dd:.2f}%", file=sys.stderr)
    print(f"\nSalvo: {fname}", file=sys.stderr)


if __name__ == "__main__":
    main()