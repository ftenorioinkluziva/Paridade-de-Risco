---
tipo: guia_pratico
categoria: "Execução"
tags:
  - paridade-de-risco
  - aporte
  - execução
  - alocação
data: 2026-06-17
status: permanente
---

# Táticas de Aporte e Distribuição

> **Resumo:** Estratégias práticas para executar aportes na carteira de paridade de risco — desde o lump sum inicial até contribuições mensais recorrentes, equilibrando precisão na alocação com simplicidade operacional.

---

## 📖 Princípios Gerais

1. **A paridade de risco só funciona com os pesos corretos.** Desvios temporários acumulados distorcem a contribuição de risco entre cenários.
2. **O CDI é seu aliado tático.** Por ter volatilidade zero, acumular temporariamente em CDI não adiciona risco à carteira — apenas a torna mais conservadora.
3. **Lotes pequenos são viáveis com corretagem zero.** O limite não é mais o custo de transação, mas o arredondamento de cotas.
4. **Não deixe o perfeito ser inimigo do bom.** Uma alocação 95% correta hoje vale mais que 100% correta daqui a 3 meses.

---

## 🚀 Cenário 1: Aporte Inicial (Lump Sum)

### Quando entra com um montante grande de uma vez

#### Estratégia recomendada: Híbrida (2 blocos)

Separa os ativos em dois grupos: os que podem ser comprados **agora** (baixo risco de marcação a mercado) e os que valem a pena **suavizar** em 2-3 entradas.

| Bloco | Ativos | Risco de M2M | % do capital | Quando executar |
|:-----:|--------|:------------:|:------------:|:---------------:|
| 🟢 **Imediato** | CDI, B5P211, Dólar, BOVA11, IB5M11 | Baixo ou peso irrelevante | ~40-50% | **Agora, de uma vez** |
| 🟡 **Parcelado** | IFRM11, XFIX11 (e outros pré-fixados ou voláteis) | Moderado | ~50-60% | **50% agora, 50% em 15-30 dias** |

#### Lote único? Também funciona

Estatisticamente, **lump sum ganha de DCA em ~2/3 dos casos** (estudo Vanguard). Na paridade de risco, onde a alocação exata é parte da tese, isso é ainda mais defensável. A versão híbrida acima é apenas um seguro comportamental contra timing adverso.

#### Fluxo sugerido

```
Semana 1:
  └── Compra CDI, B5P211, Dólar, BOVA11, IB5M11 → integral
  └── Compra 50% de IFRM11 e XFIX11

Semana 3-4:
  └── Compra 50% restante de IFRM11 e XFIX11
```

---

## 🗓️ Cenário 2: Aportes Mensais Recorrentes (R$ 5k/mês)

### Três abordagens, em ordem de preferência

### 🥇 (A) Distribuição direta nos pesos — todo mês

Distribui o valor mensal proporcionalmente aos pesos-alvo. As sobras de arredondamento de cotas vão para um caixa residual que se ajusta no mês seguinte.

**Exemplo com R$ 5.000:**

| Ativo | % alvo | R$/mês | Cota (~) | Unidades |
|-------|:------:|:------:|:--------:|:--------:|
| IFRM11 | 37,50% | R$ 1.875 | R$ 95 | 20 cotas |
| B5P211 | 18,75% | R$ 938 | R$ 82 | 11 cotas |
| XFIX11 | 14,00% | R$ 700 | R$ 92 | 8 cotas |
| CDI | 12,50% | R$ 625 | — | aporte direto |
| IB5M11 | 7,00% | R$ 350 | R$ 82 | 4 cotas |
| Dólar | 6,25% | R$ 313 | R$ 5,20 | ~USD 60 |
| BOVA11 | 4,00% | R$ 200 | R$ 105 | 2 cotas |

> ✅ **Prós:** Paridade mantida sempre, efeito "low-cost averaging" pleno
> ⚠️ **Contras:** 7 ordens/mês (~5 min com home broker)

### 🥈 (B) Acumula no CDI, distribui trimestralmente

**Mês a mês:** deposita integralmente no CDI (ou Tesouro Selic).
**A cada 3 meses:** vende o excesso de CDI e redistribui para os demais ativos.

```
Mês 1:  +R$ 5.000 em CDI (1 ordem)
Mês 2:  +R$ 5.000 em CDI (1 ordem)
Mês 3:  +R$ 5.000 em CDI (1 ordem)
        ↓
Trimestre: R$ 15.000 acumulados no CDI
        ↓
        1 sessão de compras (vende CDI, compra os 6 ativos)
```

| ✅ Prós | ⚠️ Contras |
|---------|------------|
| 1 ordem/mês (CDI) | Paridade quebra por até 3 meses |
| 1 sessão trimestral de compras | Quebra é conservadora (mais CDI = menos risco) |
| CDI rendendo > 14% → sem custo de oportunidade | Psicologicamente: vender CDI para comprar risco dói |
| Lotes maiores (ex: 60 cotas de IFRM11) | |

### 🥉 (C) Acumula nos ativos mais defasados

Alternativa avançada: a cada mês, aplica os R$ 5.000 no ativo **mais distante do peso-alvo**. Requer acompanhamento da carteira e da distância percentual.

> ⚠️ **Não recomendado:** fácil de perder o controle e acumular distorções não-intencionais. Só faz sentido se você tiver uma planilha de acompanhamento muito rigorosa.

---

## 💰 Cenário 3: Distribuição de Recursos (Resgates/Vendas)

### Quando você precisa retirar dinheiro da carteira

#### Ordem de venda (do menos prejudicial ao mais)

| Prioridade | Ativo | Razão |
|:----------:|-------|-------|
| 🥇 **1º** | CDI | Zero volatilidade, sem custo de saída. A âncora de liquidez existe para isso. |
| 🥈 **2º** | B5P211 | Duration curtíssima, baixo risco de M2M. |
| 🥉 **3º** | BOVA11 ou IB5M11 | Pesos pequenos (4% e 7%) — vender não desestrutura a carteira. |
| 4º | Dólar | Hedge cambial — só vender se precisar muito. |
| 5º | IFRM11 e XFIX11 | Maiores posições — mexer nelas distorce a paridade por mais tempo. |

#### Regra geral

Sempre recomponha a carteira após o resgate. Se vendeu CDI, os demais ativos ficaram proporcionalmente maiores — em 1-2 aportes mensais corrija.

---

## 📐 Tabela de Lotes Mínimos (por ativo)

Para planejar aportes sem fracionário:

| Ativo | Preço (~) | Lote mín. | Valor mín. prático |
|-------|:---------:|:---------:|:------------------:|
| IFRM11 | R$ 95 | 1 cota | ~R$ 95 |
| B5P211 | R$ 82 | 1 cota | ~R$ 82 |
| XFIX11 | R$ 92 | 1 cota | ~R$ 92 |
| IB5M11 | R$ 82 | 1 cota | ~R$ 82 |
| BOVA11 | R$ 105 | 1 cota | ~R$ 105 |
| Dólar | R$ 5,20 | ~USD 1 | ~R$ 5,20 |
| CDI | — | R$ 0,01 | Qualquer valor |

> 💡 **Dica:** Se o aporte mensal for muito pequeno (< R$ 500-1.000), considere a estratégia B (acumular no CDI e distribuir trimestralmente) para evitar comprar 1 cota de cada ativo por mês.

---

## ⚙️ Versão Simplificada (se você quer o mínimo de trabalho possível)

| Situação | Estratégia | Frequência |
|----------|-----------|:----------:|
| **Aporte inicial (ex: R$ 100k)** | Híbrido: R$ ativos seguros + 50% de IFRM11/XFIX11 agora, 50% em 2-3 semanas | ⏱️ 2 sessões |
| **Aporte mensal > R$ 3.000** | Distribuição direta nos pesos | 📅 Mensal |
| **Aporte mensal < R$ 3.000** | Acumula no CDI, distribui trimestralmente | 📅 Trimestral |
| **Aporte irregular (bônus, 13º)** | Tratar como lump sum pequeno — distribuição direta | ⏱️ 1 sessão |
| **Resgate** | Primeiro CDI, depois B5P211, por último IFRM11 e XFIX11 | ⏱️ 1 sessão |

---

## 📎 Notas Relacionadas

- [[Rebalanceamento Maio 2026]]
- [[Acompanhamento Junho 2026]]
- [[Carteira de paridade de risco no Brasil]]
- [[Desafio emocional da paridade de risco]]
- [[Simplificação da carteira para portfólios menores]]
- [[CDI com volatilidade zero exige premissa manual]]

---

> **Status:** 🟢 Permanente — guia de referência para execução de aportes
