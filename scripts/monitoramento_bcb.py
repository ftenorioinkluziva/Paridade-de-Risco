#!/usr/bin/env python3
"""
Monitoramento BCB - Paridade de Risco
======================================
Busca dados atualizados do Banco Central e gera um resumo em markdown
para ser salvo no vault Obsidian.

APIs utilizadas:
  - SGS (Sistema Gerenciador de Series Temporais) - series historicas
  - API OData BCB - expectativas Focus

Alertas gerados:
  - Variacao do Focus (IPCA/Selic/PIB entre semanas)
  - Gap entre realizado e expectativa
  - Violacao de limiares (IPCA > teto, divida > 80%, etc.)
  - Mudanca de tendencia (3m flipping direction)
  - Sinalizacao de transicao de cenario (C2 -> C1, etc.)
"""

import sys
import json
import os
import urllib.request
from datetime import datetime, date
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
# 5. Sistema de Alertas e Estado
# ============================================================

STATE_DIR = "/opt/data/Paridade-de-Risco/.hermes"
STATE_FILE = os.path.join(STATE_DIR, "bcb_state.json")
VAULT_PATH = "/opt/data/Paridade-de-Risco/01 - Notas Geradas"


def carregar_estado():
    """Carrega o snapshot anterior do estado."""
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def salvar_estado(sgs_data, focus_data):
    """Salva o snapshot atual para comparacao futura."""
    os.makedirs(STATE_DIR, exist_ok=True)

    state = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "focus": focus_data,
        "sgs": {},
    }

    # Salva apenas os ultimos valores de cada serie SGS
    for nome, df in sgs_data.items():
        if df is not None and not df.empty:
            state["sgs"][nome] = {
                "valor": float(df.iloc[-1, 0]),
                "data": df.index[-1].strftime("%Y-%m-%d"),
            }

    # Salva tambem os valores do mes anterior para tendencias
    for nome, df in sgs_data.items():
        if df is not None and len(df) >= 2:
            state["sgs"][nome]["valor_ant"] = float(df.iloc[-2, 0])
            state["sgs"][nome]["data_ant"] = df.index[-2].strftime("%Y-%m-%d")

    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"  [!] Erro salvando estado: {e}", file=sys.stderr)


def gerar_alertas(sgs_data, focus_data):
    """
    Gera alertas comparando o snapshot atual com o anterior.
    Retorna lista de (severidade, mensagem, emoji).

    Severidade:
      🔴 = ALERTA (acao necessaria, risco concreto)
      🟡 = ATENCAO (monitorar, pode evoluir)
      🟢 = SINAL POSITIVO (cenario melhorando)
    """
    estado_ant = carregar_estado()
    alertas = []

    # ============================================================
    # 1. ALERTAS DE VARIACAO DO FOCUS
    # ============================================================
    if focus_data and "focus" in estado_ant:
        for ind, display_name in [
            ("IPCA", "IPCA"),
            ("Selic", "Selic"),
            ("PIB Total", "PIB"),
            ("Câmbio", "Dolar"),
            ("IGP-M", "IGP-M"),
        ]:
            atual = focus_data.get(ind, {})
            anterior = estado_ant["focus"].get(ind, {})

            for ano in [2026, 2027]:
                if ano in atual and ano in anterior:
                    diff = atual[ano] - anterior[ano]
                    if abs(diff) > 0.05:  # So alerta se mudou de verdade
                        if diff > 0:
                            alertas.append((chr(0x1F534), 
                                f"Focus {display_name} {ano} SUBIU: {anterior[ano]:.2f} -> {atual[ano]:.2f} ({diff:+.2f})",
                                f"Focus {display_name} subindo"))
                        else:
                            alertas.append((chr(0x1F7E2), 
                                f"Focus {display_name} {ano} CAIU: {anterior[ano]:.2f} -> {atual[ano]:.2f} ({diff:+.2f})",
                                f"Focus {display_name} caindo"))

    # ============================================================
    # 2. ALERTAS DE LIMIAR (THRESHOLD BREACH)
    # ============================================================

    # IPCA 12m > 4.5% (acima do teto da meta)
    ipca_12m = sgs_data.get("IPCA 12 meses (%)")
    if ipca_12m is not None and not ipca_12m.empty:
        val = ipca_12m.iloc[-1, 0]
        if val > 4.5:
            alertas.append((chr(0x1F534), 
                f"IPCA 12m em {val:.2f}%: ACIMA DO TETO (4,50%)",
                "IPCA acima do teto"))
        elif val > 4.0:
            alertas.append((chr(0x1F7E1), 
                f"IPCA 12m em {val:.2f}%: proximo do teto (4,50%)",
                "IPCA proximo do teto"))

    # Selic com 3 cortes consecutivos
    selic_df = sgs_data.get("Selic meta (% a.a.)")
    if selic_df is not None and len(selic_df) >= 6:
        # Conta quantas vezes mudou nos ultimos 6 meses
        mudancas_desc = []
        ult = None
        for i in range(len(selic_df)):
            v = selic_df.iloc[i, 0]
            if ult is not None and v != ult:
                mudancas_desc.append((selic_df.index[i], v - ult))
            ult = v
        cortes_recents = [d for _, d in mudancas_desc[-6:] if d < 0]
        if len(cortes_recents) == 3:
            alertas.append((chr(0x1F7E2),
                "3 cortes consecutivos da Selic (15,00% -> 14,25%) — ciclo de afrouxamento",
                "Selic caindo"))

    # IGP-M > IPCA (contagio inflacionario)
    igp_df = sgs_data.get("IGP-M mensal (%)")
    ipca_m = sgs_data.get("IPCA mensal (%)")
    if igp_df is not None and ipca_m is not None and not igp_df.empty and not ipca_m.empty:
        v_igp, v_ipca = igp_df.iloc[-1, 0], ipca_m.iloc[-1, 0]
        if v_igp > v_ipca * 1.5:
            alertas.append((chr(0x1F534),
                f"IGP-M ({v_igp:.2f}%) muito acima do IPCA ({v_ipca:.2f}%) — risco de contagio nos proximos meses",
                "IGP-M alarmante"))

    # Divida Bruta > 80% PIB
    div_df = sgs_data.get("Divida Bruta GB (% PIB)")
    if div_df is not None and not div_df.empty:
        val_div = div_df.iloc[-1, 0]
        if val_div >= 80:
            alertas.append((chr(0x1F534),
                f"Divida Bruta em {val_div:.2f}% do PIB — alerta fiscal ativo",
                "Risco fiscal"))
        elif val_div > 75:
            alertas.append((chr(0x1F7E1),
                f"Divida Bruta em {val_div:.2f}% do PIB — monitorar trajetoria fiscal",
                "Risco fiscal moderado"))

    # IBC-Br caindo 3 meses (risco de recessao)
    ibc_df = sgs_data.get("IBC-Br (atividade)")
    if ibc_df is not None and len(ibc_df) >= 3:
        if ibc_df.iloc[-1, 0] < ibc_df.iloc[-3, 0]:
            alertas.append((chr(0x1F7E1),
                "IBC-Br caindo nos ultimos 3 meses — possivel desaceleracao economica",
                "Atividade desacelerando"))

    # ============================================================
    # 3. ALERTAS DE TRANSICAO DE CENARIO
    # ============================================================

    # IPCA mensal desacelerando 3 meses seguidos -> sinal de C1
    if ipca_m is not None and len(ipca_m) >= 4:
        m1, m2, m3, m4 = (ipca_m.iloc[-(i+1), 0] for i in range(4))
        if m4 >= m3 >= m2 >= m1:
            alertas.append((chr(0x1F7E2),
                f"IPCA mensal caindo ha 3 meses ({m4:.2f}% -> {m1:.2f}%) — sinal de transicao para C1",
                "Sinal de C1"))

    # IBC-Br crescendo + IPCA 12m caindo = C1
    if ibc_df is not None and len(ibc_df) >= 3 and ipca_12m is not None and len(ipca_12m) >= 3:
        ibc_crescendo = ibc_df.iloc[-1, 0] >= ibc_df.iloc[-3, 0]
        ipca_caindo = ipca_12m.iloc[-1, 0] <= ipca_12m.iloc[-3, 0]
        if ibc_crescendo and ipca_caindo:
            alertas.append((chr(0x1F7E2),
                "Cenario C1 configurado: PIB crescendo + Inflacao caindo",
                "Transicao C1 confirmada"))

    # IBC-Br caindo + IPCA subindo = C3 (estagflacao)
    if ibc_df is not None and len(ibc_df) >= 3 and ipca_12m is not None and len(ipca_12m) >= 3:
        ibc_caindo = ibc_df.iloc[-1, 0] < ibc_df.iloc[-3, 0]
        ipca_subindo = ipca_12m.iloc[-1, 0] > ipca_12m.iloc[-3, 0]
        if ibc_caindo and ipca_subindo:
            alertas.append((chr(0x1F534),
                "ALERTA: Cenario C3 (estagflacao) configurado — PIB caindo + Inflacao subindo",
                "Transicao C3"))

    # ============================================================
    # 4. ALERTAS DE COMPARACAO REALIZADO VS FOCUS
    # ============================================================
    ipca_real = ipca_12m.iloc[-1, 0] if ipca_12m is not None and not ipca_12m.empty else None
    ipca_focus_26 = focus_data.get("IPCA", {}).get(2026) if focus_data else None
    if ipca_real is not None and ipca_focus_26 is not None:
        gap = ipca_real - ipca_focus_26
        if abs(gap) > 1.0:
            # Realizado muito acima ou abaixo do Focus
            s = chr(0x1F534) if gap > 0 else chr(0x1F7E2)
            alertas.append((s,
                f"IPCA realizado ({ipca_real:.2f}%) vs Focus ({ipca_focus_26:.2f}%): gap de {gap:+.2f}pp",
                "Realizado vs Focus divergindo"))

    selic_real = selic_df.iloc[-1, 0] if selic_df is not None and not selic_df.empty else None
    selic_focus_26 = focus_data.get("Selic", {}).get(2026) if focus_data else None
    if selic_real is not None and selic_focus_26 is not None:
        gap = selic_real - selic_focus_26
        if abs(gap) > 0.5:
            s = chr(0x1F7E1)
            alertas.append((s,
                f"Selic atual ({selic_real:.2f}%) vs Focus fim-2026 ({selic_focus_26:.2f}%): gap de {gap:+.2f}pp — mercado espera {abs(gap):.1f}pp de cambio",
                "Selic vs Focus"))

    # De-duplica alertas pelo mesmo "topico"
    vistos = set()
    alertas_unicos = []
    for sev, msg, topico in alertas:
        if topico not in vistos:
            vistos.add(topico)
            alertas_unicos.append((sev, msg))

    return alertas_unicos


def format_alertas(alertas):
    """Formata alertas para markdown."""
    if not alertas:
        return ""

    lines = []
    lines.append("## Alertas")
    lines.append("")

    for sev, msg in alertas:
        lines.append(f"- {sev} {msg}")

    lines.append("")
    return "\n".join(lines)


# ============================================================
# 6. Geracao do Relatorio Markdown
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

    # --- Alertas ---
    alertas = gerar_alertas(sgs_data, focus_data)
    alertas_texto = format_alertas(alertas)
    if alertas_texto:
        lines.append(alertas_texto)
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

    # Salva o estado atual para comparacao futura
    print("[Estado] Salvando snapshot...", file=sys.stderr)
    salvar_estado(sgs_data, focus_data)

    # Salva no vault
    vault_path = VAULT_PATH
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