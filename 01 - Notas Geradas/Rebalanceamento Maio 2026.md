---
tipo: protocolo
categoria: "Rebalanceamento"
tags:
  - paridade-de-risco
  - rebalanceamento
  - checklist
  - maio-2026
data: 2026-05-14
fonte: "Análise da carteira real vs. modelo ideal"
tem_protocolo: true
status: aberto
---

# Rebalanceamento — Maio 2026

> **Resumo:** Checklist para aproximar a carteira real da estrutura neutra de paridade de risco, equalizando a contribuição de risco entre os 4 cenários macro. Baseado nos parâmetros documentados nas notas do vault.

---

## 📊 Situação Inicial (antes do rebalanceamento)

| Ativo | Peso atual | Instrumento | Cenário |
|-------|-----------|-------------|---------|
| BOVA11 | 5,0% | Ações | C1 |
| XFIX11 | 6,0% | FIIs | C1 |
| IB5M11 | 8,0% | IPCA+ longo | C1 |
| CDI | 20,0% | Pós-fixado | C2 |
| B5P211 | 20,0% | IPCA+ curto | C2 + C3 |
| Dólar | 6,0% | Câmbio | C3 |
| FIXA11 | 35,0% | Pré-fixado | C4 |
| **Total** | **100,0%** | | |

---

## 🎯 Modelo Ideal (pesos-alvo)

Parâmetros usados (conforme vault):

| Premissa | Valor | Fonte |
|----------|-------|-------|
| C2 fixo (CDI vol zero) | **25,00%** | [[CDI com volatilidade zero exige premissa manual]] |
| Equalização C1, C3, C4 | 2 : 1 : 3 (inverso da vol) | [[Passo 2 equaliza o risco entre cenários]] |
| C1 vol (mix risco equilibrado) | 9% | [[Volatilidade consolidada como base da carteira]] |
| C3 vol (dólar referência) | 18% | mesma |
| C4 vol (pré-fixado curto) | 6% | mesma |
| C1 interno | 16% BOVA / 56% XFIX / 28% IB5M | [[risco equilibrado versus pesos iguais no Cenário 1]] |
| C2 interno | 50% CDI / 50% B5P211 | [[Juros baixos e inflação justificam ajuste manual para IMA-B curto]] |
| C3 interno | 50% dólar / 50% B5P211 | mesma |
| C4 | 100% **IFRM11** | [[IFRM11 versus FIXA11 na parte pré-fixada]] |

### Pesos-alvo por ativo

| Ativo | Peso-alvo | Cálculo |
|-------|-----------|---------|
| **BOVA11** | **4,00%** | 25% C1 × 16% |
| **XFIX11** | **14,00%** | 25% C1 × 56% |
| **IB5M11** | **7,00%** | 25% C1 × 28% |
| **CDI** | **12,50%** | 25% C2 × 50% |
| **B5P211** | **18,75%** | 25% C2×50% + 12,5% C3×50% |
| **Dólar** | **6,25%** | 12,5% C3 × 50% |
| **IFRM11** | **37,50%** | 37,5% C4 × 100% |
| **Total** | **100,00%** | ✅ |

---

## ✅ Checklist de Operações

### 🔴 Passo 1 — Vender (fontes de capital)

- [ ] **Vender FIXA11** — vender posição integral (R$ 35.000 / cada R$ 100k de carteira)
  - Motivo: duration maior que a recomendada. O instrumento correto para C4 é IFRM11.
  - Ver [[IFRM11 versus FIXA11 na parte pré-fixada]]
- [ ] **Reduzir CDI** de 20,0% → 12,5% (−R$ 7.500 / cada R$ 100k)
  - Motivo: C2 está acima do limite de 25% (CCDI + B5P211 somam ~30% da carteira)
- [ ] **Reduzir B5P211** de 20,0% → 18,75% (−R$ 1.250 / cada R$ 100k)
  - Motivo: ajuste fino
- [ ] **Reduzir BOVA11** de 5,0% → 4,0% (−R$ 1.000 / cada R$ 100k)
  - Motivo: ajuste fino (alinhar à proporção 16% dentro de C1)
- [ ] **Reduzir IB5M11** de 8,0% → 7,0% (−R$ 1.000 / cada R$ 100k)
  - Motivo: ajuste fino (alinhar à proporção 28% dentro de C1)
- [ ] **Ajustar dólar** de 6,0% → 6,25% (+R$ 250 / cada R$ 100k)
  - Motivo: ajuste fino marginal

### 🟢 Passo 2 — Comprar (destino do capital)

- [ ] **Comprar IFRM11** — abrir posição em **37,50%** (R$ 37.500 / cada R$ 100k)
  - Instrumento correto para o bloco C4 (pré-fixado curto, duration ~0,5–1 ano)
  - Ver [[Por que prefixados curtos ajudam na recessão brasileira]]
- [ ] **Aumentar XFIX11** de 6,0% → 14,0% (+R$ 8.000 / cada R$ 100k)
  - Motivo: C1 está desbalanceado — FIIs deveriam ser 56% do bloco (maior peso)
  - Ver [[risco equilibrado versus pesos iguais no Cenário 1]]

### Fluxo de caixa (por R$ 100k de carteira)

| Operação | Valor |
|----------|-------|
| Total vendas | +R$ 45.750 |
| Total compras | −R$ 45.750 |
| **Saldo** | **R$ 0,00 ✅** |

---

## 📋 Ordem Sugerida de Execução

### Rodada 1 (prioridade máxima)

- [ ] Vender FIXA11 (integral)
- [ ] Comprar IFRM11 (integral)

> 🔑 *Troca mais importante: substituir o instrumento errado de C4 pelo correto.*

### Rodada 2 (completar IFRM11 + reserva)

- [ ] Reduzir CDI em −R$ 2.500 → completa a compra de IFRM11
- [ ] Reduzir CDI em −R$ 5.000 → reserva para XFIX11

### Rodada 3 (grandes ajustes)

- [ ] Reduzir B5P211 em −R$ 1.250
- [ ] Reduzir BOVA11 em −R$ 1.000
- [ ] Reduzir IB5M11 em −R$ 1.000
- [ ] Aumentar dólar em +R$ 250
- [ ] Aumentar XFIX11 em +R$ 8.000

---

## ✅ Verificação Pós-Rebalanceamento

### Contribuição de risco por cenário (validação)

| Cenário | Capital | Vol | Contrib. risco | % do risco total |
|---------|---------|-----|---------------|------------------|
| C1 | 25,00% | 9% | 2,25 | **33,3%** |
| C2 | 25,00% | ~0% | ~0 | **~0%** |
| C3 | 12,50% | 18% | 2,25 | **33,3%** |
| C4 | 37,50% | 6% | 2,25 | **33,3%** |

> ✅ **C1 = C3 = C4** — paridade de risco perfeita entre os cenários com volatilidade não-nula.

### Carteira final

```
┌────────────────────────────────────────────────┐
│         CARTEIRA PARIDADE DE RISCO             │
├────────────────────────────────────────────────┤
│  🟢 IFRM11 .............. 37,50%  ← C4        │
│  🟢 XFIX11 .............. 14,00%  ← C1        │
│  🟢 CDI ................. 12,50%  ← C2        │
│  🟢 B5P211 .............. 18,75%  ← C2 + C3   │
│  🟢 IB5M11 ..............  7,00%  ← C1        │
│  🟢 Dólar ...............  6,25%  ← C3        │
│  🟢 BOVA11 ..............  4,00%  ← C1        │
├────────────────────────────────────────────────┤
│  TOTAL ................. 100,00%               │
│  RISCO EQUILIBRADO entre C1, C3, C4 ✅        │
└────────────────────────────────────────────────┘
```

---

## ⚠️ Lembretes Comportamentais

- Reduzir CDI de 20% para 12,5% com Selic a 13% **parece errado** — é exatamente o [[Desafio emocional da paridade de risco]]
- O dólar com apenas 6,25% **contribui com 1/3 do risco total** (vol 18%) — o peso pequeno em capital é intencional
- Se o patrimônio for < R$ 40-50 mil, considerar a [[Simplificação da carteira para portfólios menores]] (substituir IB5M11 + B5P211 por IMAB11)
- Não precisa fazer tudo em um dia — pode dividir em 2-3 rodadas mensais

---

## 📎 Notas Relacionadas

- [[Carteira de paridade de risco no Brasil]]
- [[Passo 2 equaliza o risco entre cenários]]
- [[Passo 3 calcula pesos finais por multiplicação]]
- [[Volatilidade consolidada como base da carteira]]
- [[risco equilibrado versus pesos iguais no Cenário 1]]
- [[IFRM11 versus FIXA11 na parte pré-fixada]]
- [[CDI com volatilidade zero exige premissa manual]]
- [[Juros baixos e inflação justificam ajuste manual para IMA-B curto]]
- [[Desafio emocional da paridade de risco]]

---

> **Status:** ⬜ Aberto — aguardando execução
