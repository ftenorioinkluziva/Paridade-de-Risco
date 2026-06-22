#!/usr/bin/env python3
"""
Simulacao e Benchmark - Paridade de Risco
==========================================
Usa API Blackbox para calcular performance real da carteira.
"""
import sys, json, os, statistics
from datetime import datetime
import urllib.request

API_BASE = "https://paridaderisco.blackboxinovacao.com.br"
VAULT = "/opt/data/Paridade-de-Risco/01 - Notas Geradas"

PORTFOLIO = {
    "IFRM11": {"ticker": "FIXA11.SA", "weight": 0.375, "name": "IFRM11 (Pre)", "cenario": "C4"},
    "B5P211": {"ticker": "B5P211.SA", "weight": 0.1875, "name": "B5P211 (IMAB5)", "cenario": "C2+C3"},
    "XFIX11": {"ticker": "XFIX11.SA", "weight": 0.14, "name": "XFIX11 (IFIX)", "cenario": "C1"},
    "CDI": {"ticker": "CDI_MENSAL", "weight": 0.125, "name": "CDI", "cenario": "C2"},
    "IB5M11": {"ticker": "IB5M11.SA", "weight": 0.07, "name": "IB5M11 (IMAB5+)", "cenario": "C1"},
    "DOLAR": {"ticker": "USDBRL=X", "weight": 0.0625, "name": "Dolar", "cenario": "C3"},
    "BOVA11": {"ticker": "BOVA11.SA", "weight": 0.04, "name": "BOVA11 (Ibovespa)", "cenario": "C1"},
}


def fetch(ticker, start="2026-01-01", end="2026-06-22"):
    url = f"{API_BASE}/api/assets/prices?ticker={ticker}&from={start}&to={end}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())


def main():
    print("=== Simulacao Paridade de Risco ===\n", file=sys.stderr)

    # Buscar precos atuais
    print("[1] Precos atuais...", file=sys.stderr)
    raw = fetch("", "2026-06-22", "2026-06-22")
    current = {}
    for r in raw:
        current[r["ticker"]] = float(r["price"])
    # CDI_MENSAL nao retorna com data atual, pegar CDI diario
    cdi_diario = fetch("CDI", "2026-06-19", "2026-06-22")
    if cdi_diario:
        current["CDI_PRICE"] = float(cdi_diario[0]["price"])
    else:
        current["CDI_PRICE"] = current.get("CDI", 0)

    # Buscar historico completo
    print("[2] Historico (2026)...", file=sys.stderr)
    historico = {}
    for key, info in PORTFOLIO.items():
        ticker = info["ticker"]
        try:
            data = fetch(ticker)
            data.reverse()  # ordem cronologica
            historico[key] = data
            print(f"  {key:8s}: {len(data)} registros", file=sys.stderr)
        except Exception as e:
            print(f"  [!] {key}: {e}", file=sys.stderr)

    # Calcular retornos mensais
    print("\n[3] Calculando performance...", file=sys.stderr)
    mes_retornos = {}
    for key, data in historico.items():
        if not data:
            continue
        # Agrupar por mes e pegar ultimo preco de cada mes
        meses = {}
        for r in data:
            mes = r["priceDate"][:7]
            meses[mes] = float(r["price"])

        meses_ord = sorted(meses.keys())
        retornos = {}
        for i in range(1, len(meses_ord)):
            m_ant = meses_ord[i - 1]
            m_at = meses_ord[i]
            if meses[m_ant] > 0:
                ret = (meses[m_at] / meses[m_ant]) - 1
                retornos[m_at] = ret

        # Para CDI_MENSAL, o valor ja e percentual
        if key == "CDI":
            retornos = {}
            for m in meses_ord:
                retornos[m] = meses[m] / 100

        mes_retornos[key] = {"meses": meses_ord, "retornos": retornos, "precos": meses}

    # Simular carteira
    print("[4] Simulando carteira em paridade de risco...", file=sys.stderr)

    # Coletar todos os meses disponiveis
    todos_meses = set()
    for key, mr in mes_retornos.items():
        for m in mr["meses"]:
            if m >= "2026-01":
                todos_meses.add(m)
    meses = sorted(todos_meses)

    if len(meses) < 2:
        print("  [!] Dados insuficientes", file=sys.stderr)
        return

    portfolio = [1000.0]
    cdi_only = [1000.0]
    bova_only = [1000.0]

    for i in range(1, len(meses)):
        mes = meses[i]
        ret_p = 0
        for key, info in PORTFOLIO.items():
            w = info["weight"]
            r = mes_retornos.get(key, {}).get("retornos", {}).get(mes, 0)
            ret_p += w * r
        portfolio.append(portfolio[-1] * (1 + ret_p))

        # CDI benchmark
        r_cdi = mes_retornos.get("CDI", {}).get("retornos", {}).get(mes, 0)
        cdi_only.append(cdi_only[-1] * (1 + r_cdi))

        # BOVA11 benchmark
        r_bova = mes_retornos.get("BOVA11", {}).get("retornos", {}).get(mes, 0)
        bova_only.append(bova_only[-1] * (1 + r_bova))

    # Metricas
    ret_total = (portfolio[-1] / 1000 - 1) * 100
    ret_cdi = (cdi_only[-1] / 1000 - 1) * 100
    ret_bova = (bova_only[-1] / 1000 - 1) * 100

    rets_mensais = [(portfolio[i] / portfolio[i - 1] - 1) for i in range(1, len(portfolio))]
    if rets_mensais:
        vol_m = statistics.stdev(rets_mensais)
        vol_a = vol_m * (12 ** 0.5) * 100
        ret_a = (1 + sum(rets_mensais) / len(rets_mensais)) ** 12 - 1
    else:
        vol_a = 0
        ret_a = 0

    # Max drawdown
    peak = portfolio[0]
    max_dd = 0
    for v in portfolio:
        if v > peak:
            peak = v
        dd = (v - peak) / peak
        if dd < max_dd:
            max_dd = dd

    # Sharpe (excesso sobre CDI)
    excessos = [(portfolio[i] / portfolio[i - 1] - 1) - (cdi_only[i] / cdi_only[i - 1] - 1)
                for i in range(1, len(portfolio))]
    sharpe = (statistics.mean(excessos) / statistics.stdev(excessos) * (12 ** 0.5)
              if excessos and statistics.stdev(excessos) > 0 else 0)

    print(f"\n  Periodo: {meses[0]} a {meses[-1]} ({len(portfolio)-1} meses)", file=sys.stderr)
    print(f"  Carteira RP: {ret_total:+.2f}%", file=sys.stderr)
    print(f"  CDI: {ret_cdi:+.2f}%", file=sys.stderr)
    print(f"  BOVA11: {ret_bova:+.2f}%", file=sys.stderr)
    print(f"  Vol anual: {vol_a:.2f}%", file=sys.stderr)
    print(f"  Sharpe: {sharpe:.2f}", file=sys.stderr)
    print(f"  Max DD: {max_dd*100:.2f}%", file=sys.stderr)

    # Relatorio
    hoje = datetime.now().strftime("%Y-%m-%d")
    lines = []
    lines.append("---")
    lines.append("tipo: simulacao")
    lines.append('categoria: "Performance"')
    lines.append("tags:")
    lines.append("  - simulacao")
    lines.append("  - benchmark")
    lines.append("  - performance")
    lines.append("  - 2026")
    lines.append(f"data: {hoje}")
    lines.append("status: gerado_automaticamente")
    lines.append("---")
    lines.append("")
    lines.append(f"# Simulacao 2026 - Carteira Paridade de Risco")
    lines.append("")
    lines.append(f"> Dados reais via API Blackbox | {meses[0]} a {meses[-1]}")
    lines.append("")
    lines.append("## Performance")
    lines.append("")
    lines.append("| Metrica | Carteira RP | CDI | BOVA11 |")
    lines.append("|---------|:----------:|:---:|:------:|")
    lines.append(f"| **Retorno Total** | **{ret_total:+.2f}%** | {ret_cdi:+.2f}% | {ret_bova:+.2f}% |")
    lines.append(f"| **Retorno Anualizado** | **{ret_a*100:.2f}%** | — | — |")
    lines.append(f"| **Volatilidade (anual)** | **{vol_a:.2f}%** | ~0% | — |")
    lines.append(f"| **Sharpe** | **{sharpe:.2f}** | — | — |")
    lines.append(f"| **Max Drawdown** | **{max_dd*100:.2f}%** | 0% | — |")
    lines.append("")
    lines.append("## Evolucao Mensal")
    lines.append("")
    lines.append("| Mes | Carteira | CDI | BOVA11 |")
    lines.append("|:---:|:--------:|:---:|:-----:|")
    for i in range(len(meses)):
        lines.append(f"| {meses[i]} | {portfolio[i]:.1f} | {cdi_only[i]:.1f} | {bova_only[i]:.1f} |")
    lines.append("")
    lines.append("---")
    lines.append(f"*Pesos fixos da paridade de risco | Fonte: API Blackbox*")

    filename = f"{VAULT}/Simulacao 2026 - {hoje}.md"
    with open(filename, "w") as f:
        f.write("\n".join(lines))
    print(f"\nSalvo: {filename}", file=sys.stderr)
    print("\n".join(lines))


if __name__ == "__main__":
    main()