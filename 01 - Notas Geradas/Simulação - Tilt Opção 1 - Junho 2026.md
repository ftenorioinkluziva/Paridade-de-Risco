---
tipo: simulacao
categoria: "Ajuste Tático"
tags:
  - simulacao
  - tilt
  - opcao-1
  - paridade-de-risco
data: 2026-06-19
status: rascunho
---

# Simulação — Tilt Opção 1 (C1 Leve)

## 1. Alocação Comparada

| Ativo | Cenário | Neutro | **Tilt C1** | Δ Capital | Δ Risco |
|-------|:-------:|:------:|:-----------:|:---------:|:-------:|
| **IFRM11** 🔵 | C4 | 37,50% | **37,50%** | — | — |
| **XFIX11** 🏢 | C1 | 14,00% | **15,56%** | **+1,56%** | ↑ |
| **B5P211** 🟢 | C2+C3 | 18,75% | **16,67%** | **-2,08%** | ↓ |
| **CDI** 💰 | C2 | 12,50% | **12,50%** | — | — |
| **IB5M11** 📈 | C1 | 7,00% | **7,78%** | **+0,78%** | ↑ |
| **Dólar** 💵 | C3 | 6,25% | **5,56%** | **-0,69%** | ↓ |
| **BOVA11** 📊 | C1 | 4,00% | **4,44%** | **+0,44%** | ↑ |
| | **Total** | **100%** | **100%** | | |

## 2. Risco por Cenário

### Neutro (Base)

| Cenário | Capital | Vol | Contrib. Risco | % Risco |
|---------|:-------:|:---:|:--------------:|:-------:|
| **C1** 🌱 | 25,00% | 9% | **2,25** | **33,3%** |
| **C2** 🟡 | 25,00% | ~0% | ~0 | âncora |
| **C3** 🔴 | 12,50% | 18% | **2,25** | **33,3%** |
| **C4** 🔵 | 37,50% | 6% | **2,25** | **33,3%** |

### Tilt C1

| Cenário | Capital | Vol | Contrib. Risco | % Risco | Δ pp |
|---------|:-------:|:---:|:--------------:|:-------:|:----:|
| **C1** 🌱 | **27,78%** | 9% | **2,50** | **37,0%** | **+3,7pp** |
| **C2** 🟡 | **23,61%** | ~0% | ~0 | âncora | — |
| **C3** 🔴 | **11,11%** | 18% | **2,00** | **29,6%** | **-3,7pp** |
| **C4** 🔵 | **37,50%** | 6% | **2,25** | **33,3%** | — |

> Risco total mantido em **6,75**. Apenas a fatia entre C1 e C3 foi deslocada.

## 3. Detalhamento: Abertura do B5P211

O B5P211 atende dois cenários. Com o tilt, a repartição muda:

| Destino | Neutro | **Tilt** | Δ |
|---------|:------:|:--------:|:-:|
| B5P211 → **C2** (parcela CDI) | 12,50% | **11,11%** | -1,39% |
| B5P211 → **C3** (parcela dólar) | 6,25% | **5,56%** | -0,69% |
| **Total B5P211** | **18,75%** | **16,67%** | **-2,08%** |

## 4. Simulação de Retornos por Cenário

Simulando o impacto do tilt versus neutro em cada regime macro:

### 🟢 Se C1 se confirmar (Crescimento + Desinflação — nosso palpite)

| Componente | Neutro | Tilt | Variação | Impacto |
|------------|:------:|:----:|:--------:|:-------:|
| C1 (ações/FIIs/IPCA+) sobe +20% | 25% × 20% = +5,00% | 27,78% × 20% = +5,56% | **+0,56%** | ✅ **Ganha** |
| C4 (IFRM11) sobe +5% | 37,5% × 5% = +1,88% | 37,5% × 5% = +1,88% | — | → |
| C3 (dólar) cai -5% | 12,5% × -5% = -0,63% | 11,11% × -5% = -0,56% | +0,07% | ✅ Ganha menos negativo |
| C2 (CDI) rende 14% | 25% × 14% = +3,50% | 23,61% × 14% = +3,31% | -0,19% | ⚠️ Perde um pouco |
| **Retorno Total** | **+9,75%** | **+10,19%** | **+0,44%** | ✅ |

### 🔴 Se C3 acontecer (Estagflação — risco do tilt)

| Componente | Neutro | Tilt | Variação | Impacto |
|------------|:------:|:----:|:--------:|:-------:|
| C3 (dólar) sobe +25% | 12,5% × 25% = +3,13% | 11,11% × 25% = +2,78% | **-0,35%** | ❌ Protege menos |
| C1 (ações/FIIs) cai -15% | 25% × -15% = -3,75% | 27,78% × -15% = -4,17% | **-0,42%** | ❌ Perde mais |
| C4 (IFRM11) estável | 37,5% × 0% = 0% | 37,5% × 0% = 0% | — | → |
| C2 (CDI) rende 14% | 25% × 14% = +3,50% | 23,61% × 14% = +3,31% | -0,19% | ⚠️ |
| **Retorno Total** | **+2,88%** | **+1,92%** | **-0,96%** | ❌ |

### 🟡 Se C2 persistir (Crescimento + Inflação — igual hoje)

| Componente | Neutro | Tilt | Variação | Impacto |
|------------|:------:|:----:|:--------:|:-------:|
| C2 (CDI) rende 14% | 25% × 14% = +3,50% | 23,61% × 14% = +3,31% | -0,19% | ⚠️ |
| C1 (ações/FIIs) estável | 25% × 0% = 0% | 27,78% × 0% = 0% | — | → |
| C3 (dólar) estável | 12,5% × 0% = 0% | 11,11% × 0% = 0% | — | → |
| C4 (IFRM11) rende 13% | 37,5% × 13% = +4,88% | 37,5% × 13% = +4,88% | — | → |
| **Retorno Total** | **+8,38%** | **+8,19%** | **-0,19%** | ⚠️ Leve perda |

## 5. Resumo dos Cenários

| Cenário | Neutro | Tilt C1 | Δ | Avaliação |
|---------|:------:|:-------:|:-:|-----------|
| 🟢 **C1 se confirma** | +9,75% | **+10,19%** | **+0,44%** | ✅ Ganha |
| 🟡 **C2 persiste** (hoje) | +8,38% | **+8,19%** | **-0,19%** | ⚠️ Custo baixo |
| 🔴 **C3 acontece** | +2,88% | **+1,92%** | **-0,96%** | ❌ Risco assumido |
| 🔵 **C4 domina** | ~+5% | ~+5% | ~0% | → Neutro |

> ⚠️ O tilt adiciona +0,44% se acertarmos, mas custa -0,96% se errarmos para estagflação. **Relação risco-retorno de ~1:2.** É um tilt pequeno e assimétrico — ganha-se menos do que se perde se o cenário errado ocorrer.

## 6. Checklist de Execução

- [ ] **Vender** ~R$ 0,69 de cada R$ 100 de Dólar (C3)
- [ ] **Vender** ~R$ 2,08 de cada R$ 100 de B5P211
- [ ] **Comprar** ~R$ 1,56 de cada R$ 100 de XFIX11
- [ ] **Comprar** ~R$ 0,78 de cada R$ 100 de IB5M11
- [ ] **Comprar** ~R$ 0,44 de cada R$ 100 de BOVA11
- [ ] CDI e IFRM11 **mantidos**

> **Reavaliação em 30 dias** (julho/26): se IPCA continuar caindo, mantém ou aumenta o tilt. Se IGP-M contaminar o varejo, volta ao neutro.
