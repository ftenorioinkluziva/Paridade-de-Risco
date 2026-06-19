---
tipo: simulacao
categoria: "Ajuste Tático"
tags:
  - simulacao
  - tilt
  - opcao-2
  - intra-c1
  - paridade-de-risco
data: 2026-06-19
status: rascunho
---

# Simulação — Tilt Opção 2 (Intra-C1)

## Conceito

Em vez de deslocar risco entre cenários (como na Opção 1), esta opção **mantém a paridade perfeita** (C1 = C3 = C4 = 2,25) e apenas realoca os pesos **dentro do Cenário 1** entre seus três ativos.

> ✅ Paridade de risco **perfeitamente preservada** — zero alteração na contribuição de risco entre cenários.
> ⚠️ Impacto mais sutil — depende de como XFIX11, IB5M11 e BOVA11 se comportam diferentemente dentro do mesmo cenário macro.

---

## 1. A Lógica do Ajuste Intra-C1

No C1 (PIB crescendo + inflação caindo), os três ativos se beneficiam, mas com intensidades diferentes:

| Ativo | Hoje (C2) sofre? | Se C1 chegar, ganha? | Sensibilidade a juros |
|-------|:-----------------:|:--------------------:|:---------------------:|
| **XFIX11** (FIIs) | ⚡ Resiste — atividade firme (PIB 1,91%) sustenta aluguéis | ✅ Ganha com queda de juros | Média |
| **IB5M11** (IPCA+ longo) | ⚠️ Sofre com alta de juros — duration de ~5 anos | ✅ ✅ Ganha muito com queda de juros reais | Alta |
| **BOVA11** (ações) | 🔴 Sofre — juros 14,25% comprimem valuation | ✅ Ganha com crescimento + desinflação | Alta |

**Raciocínio do tilt:**
- **BOVA11** está mais pressionado agora e não podemos afirmar que C1 já chegou → reduzimos
- **XFIX11** é o mais resiliente no interim (atividade firme + juros caindo devagar) → aumentamos
- **IB5M11** mantido — tem o maior potencial de alta se C1 chegar, mas também a maior dor se C2 persistir

---

## 2. Alocação Comparada

### Por Ativo

| Ativo | Cenário | Neutro | **Tilt Intra-C1** | Δ |
|-------|:-------:|:------:|:-----------------:|:-:|
| **IFRM11** 🔵 | C4 | 37,50% | **37,50%** | → |
| **B5P211** 🟢 | C2+C3 | 18,75% | **18,75%** | → |
| **CDI** 💰 | C2 | 12,50% | **12,50%** | → |
| **Dólar** 💵 | C3 | 6,25% | **6,25%** | → |
| **XFIX11** 🏢 | C1 | 14,00% | **15,00%** | **+1,00%** |
| **IB5M11** 📈 | C1 | 7,00% | **7,00%** | → |
| **BOVA11** 📊 | C1 | 4,00% | **3,00%** | **-1,00%** |
| | **Total** | **100%** | **100%** | |

### Por Cenário (inalterado)

| Cenário | Capital | Vol | Contrib. Risco | % Risco | Δ |
|---------|:-------:|:---:|:--------------:|:-------:|:-:|
| **C1** 🌱 | **25,00%** | 9% | **2,25** | **33,3%** | → |
| **C2** 🟡 | **25,00%** | ~0% | ~0 | âncora | → |
| **C3** 🔴 | **12,50%** | 18% | **2,25** | **33,3%** | → |
| **C4** 🔵 | **37,50%** | 6% | **2,25** | **33,3%** | → |

> ✅ Paridade **perfeitamente mantida**: C1 = C3 = C4 = 2,25.

---

## 3. Simulação de Retornos

Cenários simulados com o comportamento **diferenciado** entre os ativos do C1:

### Hipóteses de retorno por ativo em cada cenário

| Ativo | Em C2 (hoje) | Se C1 chegar | Se C3 chegar |
|-------|:------------:|:------------:|:------------:|
| **XFIX11** 🏢 | +5% (atividade) | +20% (juros caem) | -10% (recessão) |
| **IB5M11** 📈 | -3% (juros sobem) | +25% (juros reais caem) | -15% (estresse) |
| **BOVA11** 📊 | -8% (juros comprimem) | +30% (boom) | -25% (pânico) |

### 🔴 Cenário A: C2 persiste (igual hoje) — teste real do tilt

| Ativo | Peso Neutro | Retorno | Contrib. | Peso Tilt | Retorno | Contrib. |
|-------|:-----------:|:-------:|:--------:|:---------:|:-------:|:--------:|
| XFIX11 | 14,00% | +5% | +0,70% | 15,00% | +5% | **+0,75%** |
| IB5M11 | 7,00% | -3% | -0,21% | 7,00% | -3% | -0,21% |
| BOVA11 | 4,00% | -8% | -0,32% | 3,00% | -8% | **-0,24%** |
| **C1 Total** | **25,00%** | | **+0,17%** | **25,00%** | | **+0,30%** |

| Efeito no C1 | Neutro | Tilt | Δ |
|:------------:|:------:|:----:|:-:|
| Retorno C1 | +0,17% | **+0,30%** | **+0,13%** ✅ |
| Retorno carteira total (C1+C2+C3+C4) | +8,55% | **+8,68%** | **+0,13%** |

> ✅ **Já no cenário atual, o tilt reduz perdas do C1.** Ao tirar BOVA11 (-8%) e colocar em XFIX11 (+5%), a carteira sofre menos.

### 🟢 Cenário B: C1 chega (desinflação confirmada)

| Ativo | Peso Neutro | Retorno | Contrib. | Peso Tilt | Retorno | Contrib. |
|-------|:-----------:|:-------:|:--------:|:---------:|:-------:|:--------:|
| XFIX11 | 14,00% | +20% | +2,80% | 15,00% | +20% | **+3,00%** |
| IB5M11 | 7,00% | +25% | +1,75% | 7,00% | +25% | +1,75% |
| BOVA11 | 4,00% | +30% | +1,20% | 3,00% | +30% | **+0,90%** |
| **C1 Total** | **25,00%** | | **+5,75%** | **25,00%** | | **+5,65%** |

| Efeito no C1 | Neutro | Tilt | Δ |
|:------------:|:------:|:----:|:-:|
| Retorno C1 | +5,75% | **+5,65%** | **-0,10%** ⚠️ |
| Retorno carteira total | +11,63% | **+11,53%** | **-0,10%** |

> ⚠️ **O custo de ter menos BOVA11 quando C1 chegar.** Mas é pequeno porque BOVA11 é só 4% → reduzir para 3% perde só 0,10% no retorno total.

### 🔴 Cenário C: C3 chega (estagflação)

| Ativo | Peso Neutro | Retorno | Contrib. | Peso Tilt | Retorno | Contrib. |
|-------|:-----------:|:-------:|:--------:|:---------:|:-------:|:--------:|
| XFIX11 | 14,00% | -10% | -1,40% | 15,00% | -10% | **-1,50%** |
| IB5M11 | 7,00% | -15% | -1,05% | 7,00% | -15% | -1,05% |
| BOVA11 | 4,00% | -25% | -1,00% | 3,00% | -25% | **-0,75%** |
| **C1 Total** | **25,00%** | | **-3,45%** | **25,00%** | | **-3,30%** |

| Efeito no C1 | Neutro | Tilt | Δ |
|:------------:|:------:|:----:|:-:|
| Retorno C1 | -3,45% | **-3,30%** | **+0,15%** ✅ |
| Retorno carteira total | +3,03% | **+3,18%** | **+0,15%** |

> ✅ **Em estagflação, perder menos em BOVA11 também ajuda.** XFIX11 cai menos que BOVA11, então a troca é favorável nos dois cenários ruins (C2 e C3).

---

## 4. Comparação: Opção 1 × Opção 2

| Aspecto | **Opção 1** (Tilt C1) | **Opção 2** (Intra-C1) |
|---------|:---------------------:|:----------------------:|
| **Paridade de risco** | ⚠️ Desviada (C1=37%, C3=29,6%) | ✅ **Perfeita** (33,3% cada) |
| **Se C1 chegar** | **+0,44%** 🏆 | -0,10% |
| **Se C2 persistir** | -0,19% | **+0,13%** ✅ |
| **Se C3 chegar** | **-0,96%** ❌ | **+0,15%** ✅ |
| **Complexidade** | 3 ativos mexidos (B5P211, Dólar, +C1) | 2 ativos mexidos (só dentro do C1) |
| **Custo operacional** | Moderado | Baixo |
| **Relação ganho/perda** | 1:2 (assimétrica para baixo) | **Positiva nos 3 cenários** ✅ |

---

## 5. Conclusão

A **Opção 2** é mais conservadora e **alinhada ao espírito do método** (paridade de risco):

- ✅ Preserva a equalização exata de risco entre cenários
- ✅ Melhora o retorno em **C2 (hoje)** e **C3 (estagflação)**
- ⚠️ Abre mão de apenas **0,10%** se C1 chegar
- ✅ Simples de executar: só mexe em XFIX11 e BOVA11

### Checklist de Execução (a cada R$ 100 de carteira)

| Operação | Valor |
|----------|:-----:|
| 🟢 **Comprar** XFIX11 | +R$ 1,00 |
| 🔴 **Vender** BOVA11 | -R$ 1,00 |
| → Demais ativos | Mantidos |

> 2 ordens. Nenhuma alteração nos cenários C2, C3, C4. Paridade perfeita mantida.

---

## 📎 Notas Relacionadas

- [[Simulação - Tilt Opção 1 - Junho 2026]]
- [[Acompanhamento Junho 2026]]
- [[Rebalanceamento Maio 2026]]
- [[Táticas de Aporte e Distribuição]]
- [[Carteira de paridade de risco no Brasil]]