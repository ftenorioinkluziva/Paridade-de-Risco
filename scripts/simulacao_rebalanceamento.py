#!/usr/bin/env python3
"""
Simulacao com Rebalanceamento - Paridade de Risco
==================================================
Compara:
  A) Buy & Hold (pesos fixos, sem rebalancear)
  B) Rebalanceamento mensal (volta aos pesos-alvo todo mes)
  C) Rebalanceamento + aportes mensais (R$ 5k/mes)
  D) CDI (benchmark)
"""
import sys, json, statistics
from datetime import datetime
import urllib.request

API = "https://paridaderisco.blackboxinovacao.com.br/api/assets/prices"
VAULT = "/opt/data/Paridade-de-Risco/01 - Notas Geradas"

# Pesos-alvo da paridade
ATIVOS = [
    ("IFRM11", "FIXA11.SA", 37.5),
    ("B5P211", "B5P211.SA", 18.75),
    ("XFIX11", "XFIX11.SA", 14.0),
    ("CDI", "CDI_MENSAL", 12.5),
    ("IB5M11", "IB5M11.SA", 7.0),
    ("DOLAR", "USDBRL=X", 6.25),
    ("BOVA11", "BOVA11.SA", 4.0),
]


def get(ticker, start="2021-01-01", end="2026-06-22"):
    url = f"{API}?ticker={ticker}&from={start}&to={end}"
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode())


def main():
    print("=== Simulacao com Rebalanceamento ===\n", file=sys.stderr)

    # Baixar dados
    dados = {}
    print("Baixando historico...", file=sys.stderr)
    for key, ticker, _ in ATIVOS:
        data = get(ticker)
        # Organizar por mes (primeiro preco util de cada mes)
        meses = {}
        for r in data:
            m = r["priceDate"][:7]
            if m not in meses:
                meses[m] = float(r["price"])
        dados[key] = {"raw": meses, "ord": sorted(meses.keys())}
        print(f"  {key:8s}: {len(meses)} meses", file=sys.stderr)

    # Determinar meses comuns
    all_meses = set()
    for v in dados.values():
        all_meses.update(v["ord"])
    meses = sorted(m for m in all_meses if m >= "2021-01")

    # ================================================================
    # SIMULACAO A: Buy & Hold (pesos fixos, sem rebalancear)
    # ================================================================
    print(f"\n[A] Buy & Hold - {len(meses)} meses...", file=sys.stderr)
    bh_val = 1000.0
    # Quantidade de cada ativo = peso * capital_inicial / preco_inicial
    qtds = {}
    for key, _, peso_pct in ATIVOS:
        m0 = meses[0]
        p0 = dados[key]["raw"].get(m0)
        if p0 and p0 > 0:
            qtds[key] = (peso_pct / 100 * 1000) / p0
        else:
            qtds[key] = 0

    bh_hist = [1000.0]
    cdi_hist = [1000.0]
    bova_hist = [1000.0]

    for mes in meses[1:]:
        # Calcular valor da carteira B&H
        valor = 0
        for key, _, _ in ATIVOS:
            p = dados[key]["raw"].get(mes)
            if p and p > 0:
                valor += qtds[key] * p
        bh_hist.append(valor)

        # CDI (benchmark)
        r_cdi = 0
        p_cdi_ant = dados["CDI"]["raw"].get(meses[meses.index(mes)-1])
        p_cdi = dados["CDI"]["raw"].get(mes)
        if p_cdi_ant and p_cdi:
            r_cdi = p_cdi / 100
        cdi_hist.append(cdi_hist[-1] * (1 + r_cdi))

        # BOVA11
        r_bova = 0
        p_bova_ant = dados["BOVA11"]["raw"].get(meses[meses.index(mes)-1])
        p_bova = dados["BOVA11"]["raw"].get(mes)
        if p_bova_ant and p_bova:
            r_bova = (p_bova / p_bova_ant) - 1
        bova_hist.append(bova_hist[-1] * (1 + r_bova))

    # ================================================================
    # SIMULACAO B: Rebalanceamento mensal
    # ================================================================
    print("[B] Rebalanceamento mensal...", file=sys.stderr)
    rb_val = 1000.0
    rb_hist = [1000.0]

    for mes in meses[1:]:
        # Calcular retorno do mes para cada ativo
        mes_ant = meses[meses.index(mes) - 1]
        ret_mes = 0
        for key, _, peso_pct in ATIVOS:
            p_ant = dados[key]["raw"].get(mes_ant)
            p_at = dados[key]["raw"].get(mes)
            if p_ant and p_at and p_ant > 0:
                if key == "CDI":
                    ret = p_at / 100  # CDI_MENSAL = percentual do mes
                else:
                    ret = (p_at / p_ant) - 1
                ret_mes += (peso_pct / 100) * ret

        rb_val *= (1 + ret_mes)
        rb_hist.append(rb_val)

    # ================================================================
    # SIMULACAO C: Rebalanceamento + aporte mensal (simplificado)
    # ================================================================
    print("[C] Rebalanceamento + aporte R$ 5k/mes...", file=sys.stderr)
    aporte_mensal = 5000
    rc_val = 0.0
    rc_hist = [0.0]
    total_investido = 0.0

    for i, mes in enumerate(meses):
        if i == 0:
            # Primeiro mes: apenas aporte
            rc_val = aporte_mensal
            total_investido = aporte_mensal
        else:
            mes_ant = meses[i - 1]
            # Calcular retorno do mes (mesma formula do rebalanceamento B)
            ret_mes = 0.0
            for key, _, peso_pct in ATIVOS:
                p_ant = dados[key]["raw"].get(mes_ant)
                p_at = dados[key]["raw"].get(mes)
                if p_ant and p_at and p_ant > 0:
                    if key == "CDI":
                        ret = p_at / 100
                    else:
                        ret = (p_at / p_ant) - 1
                    ret_mes += (peso_pct / 100) * ret

            # Aplicar retorno e depois aporte
            rc_val = rc_val * (1 + ret_mes) + aporte_mensal
            total_investido += aporte_mensal

        rc_hist.append(rc_val)

    # ================================================================
    # METRICAS
    # ================================================================
    def calc_metricas(hist, cdi_hist, bova_hist, label):
        n = len(hist) - 1
        ret_tot = (hist[-1] / hist[0] - 1) * 100
        anos = n / 12
        ret_a = ((hist[-1] / hist[0]) ** (1 / anos) - 1) * 100 if anos > 0 else 0
        ret_cdi = (cdi_hist[-1] / cdi_hist[0] - 1) * 100
        ret_bova = (bova_hist[-1] / bova_hist[0] - 1) * 100

        rets_m = [(hist[i] / hist[i-1] - 1) for i in range(1, len(hist))]
        vol_a = (statistics.stdev(rets_m) * (12 ** 0.5) * 100) if rets_m else 0

        peak = hist[0]
        max_dd = 0
        for v in hist:
            if v > peak:
                peak = v
            dd = (v - peak) / peak * 100
            if dd < max_dd:
                max_dd = dd

        # CDI+ (premio sobre CDI)
        premio = ret_tot - ret_cdi

        print(f"\n{'='*55}", file=sys.stderr)
        print(f"  {label}", file=sys.stderr)
        print(f"{'='*55}", file=sys.stderr)
        print(f"  Retorno Total:     {ret_tot:+.2f}% ({ret_a:.2f}% a.a.)", file=sys.stderr)
        print(f"  vs CDI:            {ret_cdi:+.2f}%  -> Premio: {premio:+.2f}pp", file=sys.stderr)
        print(f"  vs BOVA11:         {ret_bova:+.2f}%", file=sys.stderr)
        print(f"  Volatilidade:      {vol_a:.2f}% a.a.", file=sys.stderr)
        print(f"  Max Drawdown:      {max_dd:.2f}%", file=sys.stderr)
        return ret_tot, ret_a, premio, vol_a, max_dd, rets_m

    print(file=sys.stderr)
    m_bh = calc_metricas(bh_hist, cdi_hist, bova_hist, "A) Buy & Hold (pesos fixos)")
    m_rb = calc_metricas(rb_hist, cdi_hist, bova_hist, "B) Rebalanceamento mensal")

    # CDI acumulado e investido total para C
    ret_cdi_total = (cdi_hist[-1] / cdi_hist[0] - 1) * 100
    premio_c = rc_hist[-1] - total_investido
    premio_c_pct = (premio_c / total_investido) * 100

    # Resumo C
    print(f"\n{'='*55}", file=sys.stderr)
    print(f"  C) Rebalanceamento + aporte R$ 5k/mes", file=sys.stderr)
    print(f"{'='*55}", file=sys.stderr)
    print(f"  Total investido: R$ {total_investido:.0f}", file=sys.stderr)
    print(f"  Patrimonio final: R$ {rc_hist[-1]:.0f}", file=sys.stderr)
    print(f"  Ganho: R$ {premio_c:.0f} ({premio_c_pct:.2f}%)", file=sys.stderr)
    print(f"  Meses: {len(rc_hist)-1}", file=sys.stderr)

    # ================================================================
    # RELATORIO
    # ================================================================
    hoje = datetime.now().strftime("%Y-%m-%d")
    L = []
    L.append("---")
    L.append("tipo: simulacao")
    L.append('categoria: "Rebalanceamento"')
    L.append("tags:")
    L.append("  - simulacao")
    L.append("  - rebalanceamento")
    L.append("  - aporte")
    L.append("  - 5-anos")
    L.append(f"data: {hoje}")
    L.append("status: gerado_automaticamente")
    L.append("---")
    L.append("")
    L.append("# Simulacao com Rebalanceamento")
    L.append("")
    L.append(f"> {meses[0]} a {meses[-1]} | Dados via API Blackbox")
    L.append("")

    L.append("## Comparacao das Estrategias")
    L.append("")
    L.append("| Metrica | A) Buy & Hold | B) Rebalanceamento |")
    L.append("|--------|:------------:|:-----------------:|")
    L.append(f"| Retorno Total | **{m_bh[0]:+.2f}%** | **{m_rb[0]:+.2f}%** |")
    L.append(f"| Retorno Anual | **{m_bh[1]:.2f}%** | **{m_rb[1]:.2f}%** |")
    L.append(f"| Premio vs CDI | **{m_bh[2]:+.2f}pp** | **{m_rb[2]:+.2f}pp** |")
    L.append(f"| Volatilidade | **{m_bh[3]:.2f}%** | **{m_rb[3]:.2f}%** |")
    L.append(f"| Max Drawdown | **{m_bh[4]:.2f}%** | **{m_rb[4]:.2f}%** |")
    L.append("")
    L.append(f"> C) Com aportes de R$ {aporte_mensal:.0f}/mes: Investiu R$ {total_investido:.0f}, Patrimonio R$ {rc_hist[-1]:.0f}, Ganho R$ {premio_c:.0f} ({premio_c_pct:.1f}%)")
    L.append("")

    L.append("## Retorno Anual (com rebalanceamento)")
    L.append("")
    L.append("| Ano | Carteira (Rebal) | CDI | Premio CDI+ |")
    L.append("|:---:|:----------------:|:---:|:-----------:|")

    # Calcular retornos anuais para B (rebalanceamento)
    for a in range(2021, 2027):
        m_ano = [m for m in meses if m.startswith(str(a))]
        if len(m_ano) < 2:
            continue
        i0 = meses.index(m_ano[0])
        i1 = meses.index(m_ano[-1])
        ret = (rb_hist[i1] / rb_hist[i0] - 1) * 100
        ret_c = (cdi_hist[i1] / cdi_hist[i0] - 1) * 100
        premio = ret - ret_c
        L.append(f"| **{a}** | {ret:+.2f}% | {ret_c:+.2f}% | {premio:+.2f}pp |")
    L.append("")

    # Conclusao
    L.append("## Conclusao")
    L.append("")
    L.append("| Aspecto | Resultado |")
    L.append("|---------|----------|")
    L.append(f"| Rebalanceamento vs Buy & Hold | {'Ganha' if m_rb[0] > m_bh[0] else 'Perde'} {abs(m_rb[0]-m_bh[0]):+.2f}pp |")
    L.append(f"| Premio CDI+ (Rebalanceado) | {m_rb[2]:+.2f}pp no periodo |")
    L.append(f"| Volatilidade | {m_rb[3]:.2f}% a.a. |")
    L.append(f"| Maior queda | {m_rb[4]:.2f}% |")
    L.append(f"| Aportes mensais geraram | R$ {premio_c:.0f} de ganho sobre R$ {total_investido:.0f} investidos |")
    L.append("")

    L.append("---")
    L.append(f"*Pesos-alvo da paridade de risco | Fonte: API Blackbox*")

    fname = f"{VAULT}/Simulacao Rebalanceamento - {hoje}.md"
    with open(fname, "w") as f:
        f.write("\n".join(L))
    print(f"\nSalvo: {fname}", file=sys.stderr)


if __name__ == "__main__":
    main()