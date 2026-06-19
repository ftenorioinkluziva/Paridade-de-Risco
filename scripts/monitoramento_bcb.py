#!/usr/bin/env python3
"""
Monitoramento BCB - Paridade de Risco
======================================
Busca dados atualizados do Banco Central e gera um resumo em markdown
para ser salvo no vault Obsidian.

APIs utilizadas:
  - SGS (Sistema Gerenciador de Series Temporais) - series historicas
  - API REST do BCB - expectativas Focus (fallback gracioso)
"""

import sys
import json
import urllib.request
from datetime import datetime
import pandas as pd

pd.set_option("display.max_columns", 20)
pd.set_option("display.width", 120)

from bcb import sgs


# ============================================================
# 1. SGS - Series Temporais
# ============================================================

SERIES = {
    "IPCA mensal (%)": 433,
    "IPCA 12 meses (%)": 13522,
    "Selic meta (% a.a.)": 432,
    "IBC-Br (atividade)": 24363,
    "Dolar Ptax (R$)": 3698,
    "IGP-M mensal (%)": 189,
    "Divida Bruta GB (% PIB)": 13762,
}


def fetch_sgs(timeout=90):
    """Busca todas as series SGS."""
    results = {}
    for nome, cod in SERIES.items():
        try:
            df = sgs.get(cod, start="2025-06-01", end="2026-06-19", timeout=timeout)
            if df is not None and not df.empty:
                results[nome] = df
                print(f"  [+] {nome} ({cod}): {len(df)} registros", file=sys.stderr)
            else:
                print(f"  [-] {nome} ({cod}): vazio", file=sys.stderr)
        except Exception as e:
            print(f"  [!] {nome} ({cod}): {str(e)[:100]}", file=sys.stderr)
    return results


def tendencia(df, janela=1):
    """Calcula tendencia comparando ultimo com janela anterior."""
    if df is None or len(df) < janela + 1:
        return "-"
    v1 = df.iloc[-1, 0]
    v2 = df.iloc[-(janela + 1), 0]
    if v1 > v2:
        return chr(0x1F534) + " ↑"  # 🔴
    elif v1 < v2:
        return chr(0x1F7E2) + " ↓"  # 🟢
    return chr(0x26AA) + " →"       # ⚪


def ultimo_valor(df):
    """Retorna (data_str, valor) do ultimo registro."""
    if df is None or df.empty:
        return ("-", None)
    return (df.index[-1].strftime("%d/%m/%y"), df.iloc[-1, 0])


# ============================================================
# 2. Focus - API REST direta
# ============================================================

FOCUS_API_URL = (
    "https://olinda.bcb.gov.br/olinda/servico/Expectativas/"
    "versao/v1/odata/ExpectativasMercadoAnuais"
)

INDICADORES_FOCUS = ["IPCA", "Selic", "PIB Total", "Câmbio", "IGP-M"]


def fetch_focus(timeout=30):
    """
    Busca expectativas Focus via OData do BCB.
    Usa %24 no lugar de $ para compatibilidade com urlencode.
    Retorna dicionario {Indicador: {ano: mediana}}.
    """
    from urllib.parse import urlencode, quote
    from collections import defaultdict

    # Usa DataReferencia (string ano) e filtra anos 2025-2030
    # Ordena por Data descendente para pegar o Focus mais recente
    params = {
        "%24format": "json",
        "%24top": 500,
        "%24filter": (
            "Indicador eq 'IPCA' or Indicador eq 'Selic' or "
            "Indicador eq 'PIB Total' or Indicador eq 'Câmbio' or "
            "Indicador eq 'IGP-M'"
        ),
        "%24orderby": "Data desc",
    }

    # Constroi a URL manualmente para maior controle
    param_parts = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
    url = f"{FOCUS_API_URL}?{param_parts}"

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
            values = data.get("value", [])
    except Exception as e:
        print(f"  [!] Focus API: {str(e)[:80]}", file=sys.stderr)
        print("  [i] As series SGS foram coletadas com sucesso!", file=sys.stderr)
        return {}

    if not values:
        print("  [-] Focus: nenhum registro encontrado", file=sys.stderr)
        return {}

    # Agrupa por Indicador + DataReferencia (ano)
    # Pega a ultima mediana de cada ano (a mais recente)
    grupos = defaultdict(dict)
    for v in values:
        ind = v.get("Indicador", "")
        ref = v.get("DataReferencia", "")
        med = v.get("Mediana")
        if not ind or not ref or med is None:
            continue
        # So nos interessa 2025-2030
        try:
            ano = int(ref)
            if ano < 2025 or ano > 2030:
                continue
        except ValueError:
            continue
        # Sobrescreve com o valor mais recente (ordenado por Data desc)
        if ano not in grupos[ind]:
            grupos[ind][ano] = med

    results = {}
    for ind in INDICADORES_FOCUS:
        if ind in grupos and grupos[ind]:
            anos = sorted(grupos[ind].keys())
            dados = {a: grupos[ind][a] for a in anos}
            results[ind] = dados
            print(f"  [+] Focus {ind}: {dados}", file=sys.stderr)
        else:
            print(f"  [-] Focus {ind}: sem dados", file=sys.stderr)

    if not results:
        print("  [i] Nenhum dado Focus disponivel no momento", file=sys.stderr)

    return results


def format_focus_table(focus_data):
    """Formata expectativas Focus em markdown."""
    if not focus_data:
        return (
            "*Dados Focus indisponiveis no momento. "
            "Tente novamente mais tarde.*\n"
        )

    anos = sorted(set(
        a for dados in focus_data.values() for a in dados.keys()
    ))

    if not anos:
        return "*Nenhum dado de expectativas disponivel.*\n"

    lines = []
    lines.append("| Indicador | " + " | ".join(f"**{a}**" for a in anos) + " |")
    lines.append("|" + "|".join(":---:" for _ in range(len(anos) + 1)) + "|")

    # Mostra Cambio como Dolar no relatorio
    display_names = {
        "IPCA": "IPCA",
        "Selic": "Selic",
        "PIB Total": "PIB Total",
        "Câmbio": "Dólar",
        "IGP-M": "IGP-M",
    }

    for ind in INDICADORES_FOCUS:
        if ind not in focus_data:
            continue
        nome = display_names.get(ind, ind)
        dados = focus_data[ind]
        vals = []
        for a in anos:
            if a in dados:
                vals.append(f"{dados[a]:.2f}")
            else:
                vals.append("-")
        lines.append(f"| {nome} | " + " | ".join(vals) + " |")

    return "\n".join(lines)


# ============================================================
# 3. Classificacao do Cenário
# ============================================================

def classificar_cenario(sgs_data):
    """Classifica o cenario macro com base nos dados disponiveis."""
    ipca_12m = sgs_data.get("IPCA 12 meses (%)")
    ibc_br = sgs_data.get("IBC-Br (atividade)")
    selic = sgs_data.get("Selic meta (% a.a.)")

    # Fallback se dados insuficientes
    if ipca_12m is None or len(ipca_12m) < 2:
        return "Dados insuficientes para classificacao (IPCA 12m indisponivel)\n"
    if ibc_br is None or len(ibc_br) < 3:
        # Tenta com 2 dados
        if ibc_br is not None and len(ibc_br) >= 2:
            ibc_crescendo = ibc_br.iloc[-1, 0] > ibc_br.iloc[-2, 0]
        else:
            return "Dados insuficientes para classificacao (IBC-Br indisponivel)\n"
    else:
        # Compara 3 meses para suavizar ruido
        ibc_crescendo = ibc_br.iloc[-1, 0] > ibc_br.iloc[-3, 0]

    # Inflacao: IPCA 12m tendencia (comparar ultimos 3 pontos)
    if len(ipca_12m) >= 3:
        inf_subindo = ipca_12m.iloc[-1, 0] > ipca_12m.iloc[-3, 0]
    else:
        inf_subindo = ipca_12m.iloc[-1, 0] > ipca_12m.iloc[-2, 0]

    ipca_val = ipca_12m.iloc[-1, 0]

    # Status da meta
    if ipca_val > 4.5:
        meta_str = chr(0x1F534) + " Acima do teto (>4,50%)"
    elif ipca_val >= 1.5:
        meta_str = chr(0x1F7E2) + " Dentro do intervalo (1,50%-4,50%)"
    else:
        meta_str = chr(0x1F535) + " Abaixo do intervalo (<1,50%)"

    pib_str = chr(0x1F7E2) + " **CRESCENDO**" if ibc_crescendo else chr(0x1F534) + " **CAINDO**"
    inf_str = chr(0x1F534) + " **SUBINDO**" if inf_subindo else chr(0x1F7E2) + " **CAINDO**"

    if ibc_crescendo and not inf_subindo:
        linhas = [
            chr(0x1F7E2) + " **Cenario Atual: C1**  --  **Crescimento + Desinflacao**",
            "",
            "**Ativo favorecido:** Acoes (BOVA11), FIIs (XFIX11), IPCA+ longo (IB5M11)",
        ]
    elif ibc_crescendo and inf_subindo:
        linhas = [
            chr(0x1F7E1) + " **Cenario Atual: C2**  --  **Crescimento + Inflacao**",
            "",
            "**Ativo favorecido:** CDI / Tesouro Selic",
        ]
    elif not ibc_crescendo and inf_subindo:
        linhas = [
            chr(0x1F534) + " **Cenario Atual: C3**  --  **Estagflacao**",
            "",
            "**Ativo favorecido:** Dolar",
        ]
    else:
        linhas = [
            chr(0x1F535) + " **Cenario Atual: C4**  --  **Recessao**",
            "",
            "**Ativo favorecido:** Pre-fixado curto (IFRM11)",
        ]

    linhas += [
        "",
        "| Variavel | Tendencia | Meta / Referencia |",
        "|----------|:---------:|:-----------------:|",
        f"| **PIB** (IBC-Br) | {pib_str} | -- |",
        f"| **Inflacao** (IPCA 12m: {ipca_val:.2f}%) | {inf_str} | {meta_str} |",
    ]

    return "\n".join(linhas) + "\n"


# ============================================================
# 4. Geracao do Relatorio Markdown
# ============================================================

def gerar_relatorio(sgs_data, focus_data):
    """Gera o relatorio markdown completo."""
    hoje = datetime.now()
    data_str = hoje.strftime("%d/%m/%Y")
    hora_str = hoje.strftime("%H:%M")

    lines = []
    lines.append("---")
    lines.append("tipo: monitoramento")
    lines.append('categoria: "Macro"')
    lines.append("tags:")
    lines.append("  - monitoramento")
    lines.append("  - bcb")
    lines.append("  - cenário")
    lines.append(f"data: {hoje.strftime('%Y-%m-%d')}")
    lines.append("status: gerado_automaticamente")
    lines.append("---")
    lines.append("")
    lines.append(f"# Monitoramento BCB - {data_str}")
    lines.append("")
    lines.append(f"> Gerado automaticamente via **python-bcb** | {hora_str}")
    lines.append("")

    # --- Cenário ---
    lines.append("## Classificacao do Cenário")
    lines.append("")
    lines.append(classificar_cenario(sgs_data))
    lines.append("")

    # --- Tabela de Series ---
    lines.append("## Indicadores Macroeconomicos")
    lines.append("")
    lines.append("| Indicador | Ultima data | Valor | Tendencia (1m) | Tendencia (3m) |")
    lines.append("|-----------|:-----------:|:----:|:--------------:|:--------------:|")

    ordem = [
        "Selic meta (% a.a.)",
        "IPCA mensal (%)",
        "IPCA 12 meses (%)",
        "IBC-Br (atividade)",
        "Dolar Ptax (R$)",
        "IGP-M mensal (%)",
        "Divida Bruta GB (% PIB)",
    ]

    for nome in ordem:
        if nome in sgs_data:
            df = sgs_data[nome]
            data, val = ultimo_valor(df)
            if val is not None:
                t1 = tendencia(df, 1)
                t3 = tendencia(df, 3)
                lines.append(f"| {nome} | {data} | {val:.2f} | {t1} | {t3} |")

    lines.append("")

    # --- Indicadores Calculados ---
    linhas_calc = []
    selic_df = sgs_data.get("Selic meta (% a.a.)")
    ipca_12m_df = sgs_data.get("IPCA 12 meses (%)")
    ipca_m_df = sgs_data.get("IPCA mensal (%)")
    ibc_df = sgs_data.get("IBC-Br (atividade)")
    igp_df = sgs_data.get("IGP-M mensal (%)")

    if selic_df is not None and ipca_12m_df is not None:
        selic_v = selic_df.iloc[-1, 0]
        ipca_v = ipca_12m_df.iloc[-1, 0]
        juro_real = selic_v - ipca_v
        s = chr(0x1F7E2) if juro_real > 0 else chr(0x1F534)
        linhas_calc.append(
            f"- **Juro real:** {s} Selic {selic_v:.2f}% - IPCA 12m {ipca_v:.2f}%"
            f" = **{juro_real:.2f}%** a.a."
        )

    if ibc_df is not None and len(ibc_df) >= 3:
        v_3m = ibc_df.iloc[-3, 0]
        v_now = ibc_df.iloc[-1, 0]
        var = (v_now / v_3m - 1) * 100
        s = chr(0x1F7E2) if var > 0 else chr(0x1F534)
        linhas_calc.append(f"- **IBC-Br (3 meses):** {s} {v_3m:.2f} -> {v_now:.2f} ({var:+.2f}%)")

    if ipca_m_df is not None and igp_df is not None and not ipca_m_df.empty and not igp_df.empty:
        v_ipca = ipca_m_df.iloc[-1, 0]
        v_igp = igp_df.iloc[-1, 0]
        diff = v_igp - v_ipca
        s = chr(0x1F534) if diff > 0 else chr(0x1F7E2)
        linhas_calc.append(
            f"- **IGP-M x IPCA:** {s} IGP-M {v_igp:.2f}% vs IPCA {v_ipca:.2f}%"
            f" (dif: {diff:+.2f}pp)"
        )

    if ipca_m_df is not None and len(ipca_m_df) >= 3:
        v_ant, v_atual = ipca_m_df.iloc[-3, 0], ipca_m_df.iloc[-1, 0]
        s = chr(0x1F7E2) if v_ant >= v_atual else chr(0x1F534)
        linhas_calc.append(f"- **Tendencia IPCA (3m):** {s} {v_ant:.2f}% -> {v_atual:.2f}%")

    if linhas_calc:
        lines.append("### Indicadores Calculados")
        lines.append("")
        lines.extend(linhas_calc)
        lines.append("")

    # --- Focus ---
    lines.append("## Expectativas de Mercado (Focus)")
    lines.append("")
    lines.append("> Boletim Focus - Mediana das expectativas de mercado")
    lines.append("")
    lines.append(format_focus_table(focus_data))
    lines.append("")

    # --- Selic / Copom ---
    if selic_df is not None and not selic_df.empty:
        lines.append("## Reunioes do Copom")
        lines.append("")
        lines.append("| Data | Selic Meta | Variacao |")
        lines.append("|:----:|:----------:|:--------:|")

        # Filtrar apenas dias com mudanca de valor
        valores = []
        for i in range(len(selic_df)):
            val = selic_df.iloc[i, 0]
            if i == 0 or val != selic_df.iloc[i - 1, 0]:
                valores.append((selic_df.index[i], val))

        # Mostrar as ultimas mudancas
        for i_data, (data, val) in enumerate(valores[-6:]):
            var = ""
            if i_data > 0:
                v_prev = valores[-6:][i_data - 1][1]
                diff = val - v_prev
                if diff > 0:
                    var = chr(0x1F534) + f" +{diff:.2f}"
                elif diff < 0:
                    var = chr(0x1F7E2) + f" {diff:.2f}"
                else:
                    var = chr(0x26AA)

            lines.append(f"| {data.strftime('%d/%m/%y')} | {val:.2f}% | {var} |")

    lines.append("")

    # --- Footer ---
    lines.append("---")
    lines.append(f"*Gerado em {data_str} as {hora_str} via python-bcb (SGS + API BCB)*")
    lines.append("")

    return "\n".join(lines)


# ============================================================
# 5. Main
# ============================================================

def main():
    print("Buscando dados do Banco Central...\n", file=sys.stderr)

    print("[SGS] Series temporais...", file=sys.stderr)
    sgs_data = fetch_sgs()

    print("\n[Focus] Expectativas de mercado...", file=sys.stderr)
    focus_data = fetch_focus()

    print("\n[Relatorio] Gerando markdown...", file=sys.stderr)
    relatorio = gerar_relatorio(sgs_data, focus_data)

    # Salva no vault
    vault_path = "/opt/data/Paridade-de-Risco/01 - Notas Geradas"
    hoje = datetime.now()
    filename = f"{vault_path}/Monitoramento BCB - {hoje.strftime('%Y-%m-%d')}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(relatorio)

    print(f"\nSalvo: {filename}", file=sys.stderr)
    print(f"Tamanho: {len(relatorio)} chars", file=sys.stderr)

    # Imprime no stdout para uso em cron job
    print(relatorio)


if __name__ == "__main__":
    main()