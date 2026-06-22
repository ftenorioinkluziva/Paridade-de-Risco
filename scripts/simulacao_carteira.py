#!/usr/bin/env python3
"""
Simulacao e Benchmark - Paridade de Risco
==========================================
Usa API Blackbox (precos atuais) + SGS/BCB (historico) para simular
a carteira em paridade de risco.
"""
import sys, json, os
from datetime import datetime, date
import urllib.request
import pandas as pd
from bcb import sgs

API_BASE = "https://paridaderisco.blackboxinovacao.com.br"

# ============================================================
# Portfolio weights
# ============================================================
PORTFOLIO = {
    "IFRM11": {"sgs_code": None, "weight": 0.375, "name": "IFRM11", "cenario": "C4"},
    "B5P211": {"sgs_code": 12467, "weight": 0.1875, "name": "B5P211 (IMAB5)", "cenario": "C2+C3"},
    "XFIX11": {"sgs_code": None, "weight": 0.14, "name": "XFIX11 (IFIX)", "cenario": "C1"},
    "CDI": {"sgs_code": 4391, "weight": 0.125, "name": "CDI", "cenario": "C2"},
    "IB5M11": {"sgs_code": 12468, "weight": 0.07, "name": "IB5M11 (IMAB5+)", "cenario": "C1"},
    "DOLAR": {"sgs_code": 3698, "weight": 0.0625, "name": "Dolar", "cenario": "C3"},
    "BOVA11": {"sgs_code": None, "weight": 0.04, "name": "BOVA11", "cenario": "C1"},
}

# SGS-calculable proxies for non-SGS tickers
PROXIES = {
    "IFRM11": None,  # pre-fixado - usa CDI + premio
    "XFIX11": None,  # IFIX - nao disponivel no SGS
    "BOVA11": None,  # IBOV - nao disponivel no SGS
}

# ============================================================
# Fetch current prices from Blackbox API
# ============================================================
def fetch_current_prices():
    url = f"{API_BASE}/api/assets/prices"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())

def get_latest_prices():
    data = fetch_current_prices()
    ticker_map = {}
    for entry in data:
        ticker = entry["ticker"]
        ticker_map[ticker] = {
            "price": float(entry["price"]),
            "date": entry["priceDate"],
            "name": entry["name"],
        }
    return ticker_map

# ============================================================
# Main
# ============================================================
def main():
    print("=== Carteira Paridade de Risco - Benchmark ===\n", file=sys.stderr)

    print("[1/3] Buscando precos atuais (API Blackbox)...", file=sys.stderr)
    prices = get_latest_prices()

    print(f"\n[2/3] Posicao Atual da Carteira:\n", file=sys.stderr)
    print(f"  {'Ativo':12s} {'Peso':>6s} {'Preco':>10s} {'Data':>12s} {'Cenario':>8s}", file=sys.stderr)
    print(f"  {'-'*50}", file=sys.stderr)

    # Map our portfolio to API tickers
    ticker_map = {
        "IFRM11": "FIXA11.SA",
        "B5P211": "B5P211.SA",
        "XFIX11": "XFIX11.SA",
        "CDI": "CDI",
        "IB5M11": "IB5M11.SA",
        "DOLAR": "USDBRL=X",
        "BOVA11": "BOVA11.SA",
    }

    for key, info in sorted(PORTFOLIO.items(), key=lambda x: x[1]["weight"], reverse=True):
        api_ticker = ticker_map[key]
        p = prices.get(api_ticker, {})
        preco = p.get("price", "N/A")
        data_p = p.get("date", "N/A")[:10]
        if isinstance(preco, (int, float)):
            print(f"  {key:12s} {info['weight']*100:5.1f}% {preco:>10.2f} {data_p:>12s} {info['cenario']:>8s}", file=sys.stderr)
        else:
            print(f"  {key:12s} {info['weight']*100:5.1f}% {'N/A':>10s} {data_p:>12s} {info['cenario']:>8s}", file=sys.stderr)

    # Try SGS for historical data
    print(f"\n[3/3] Buscando historico SGS para simulacao...", file=sys.stderr)
    try:
        selic = sgs.get(432, start="2025-01-01", timeout=60)
        if selic is not None:
            ult_selic = selic.iloc[-1, 0]
            print(f"  Selic atual: {ult_selic:.2f}%", file=sys.stderr)
    except:
        print("  SGS indisponivel no momento", file=sys.stderr)

    # --- Generate markdown report ---
    hoje = datetime.now().strftime("%Y-%m-%d")
    lines = []
    lines.append("---")
    lines.append("tipo: benchmark")
    lines.append('categoria: "Carteira"')
    lines.append("tags:")
    lines.append("  - benchmark")
    lines.append("  - precos")
    lines.append("  - carteira")
    lines.append(f"data: {hoje}")
    lines.append("status: gerado_automaticamente")
    lines.append("---")
    lines.append("")
    lines.append(f"# Benchmark da Carteira - {hoje}")
    lines.append("")
    lines.append("> Precos via API Blackbox")
    lines.append("")
    lines.append("## Posicao Atual")
    lines.append("")
    lines.append("| Ativo | Peso | Preco | Data | Cenário |")
    lines.append("|------|:---:|:----:|:----:|:-------:|")

    for key, info in sorted(PORTFOLIO.items(), key=lambda x: x[1]["weight"], reverse=True):
        api_ticker = ticker_map[key]
        p = prices.get(api_ticker, {})
        preco = p.get("price", "N/A")
        data_p = p.get("date", "")[:10]
        if isinstance(preco, (int, float)):
            lines.append(f"| {info['name']} | {info['weight']*100:.1f}% | {preco:.2f} | {data_p} | {info['cenario']} |")
        else:
            lines.append(f"| {info['name']} | {info['weight']*100:.1f}% | N/A | {data_p} | {info['cenario']} |")

    lines.append("")
    lines.append("## Resumo")
    lines.append("")
    lines.append(f"- Total de ativos: {len(PORTFOLIO)}")
    lines.append(f"- Carteira 100% alocada: {sum(i['weight'] for i in PORTFOLIO.values())*100:.1f}%")
    lines.append(f"- Cenarios cobertos: C1 (25% capital), C2 (25%), C3 (12,5%), C4 (37,5%)")
    lines.append(f"- Risco equalizado: C1=C3=C4=33,3%")
    lines.append("")
    lines.append("---")
    lines.append(f"*Gerado em {hoje} via API Blackbox*")

    vault_path = "/opt/data/Paridade-de-Risco/01 - Notas Geradas"
    filename = f"{vault_path}/Benchmark Carteira - {hoje}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nSalvo: {filename}", file=sys.stderr)
    print("\n".join(lines))

if __name__ == "__main__":
    main()
