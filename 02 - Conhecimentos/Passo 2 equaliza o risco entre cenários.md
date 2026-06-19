---
tipo: conhecimento
categoria: "Construção de Carteira"
tags:
  - passo-2
  - equalizacao-de-risco
  - cenarios
  - volatilidade
fonte: "Cálculo de Pesos para Carteira Paridade de Risco Brasil"
pdf: "[[Cálculo de Pesos para Carteira Paridade de Risco Brasil.pdf]]"
nota_fonte: "[[Cálculo de Pesos para Carteira Paridade de Risco Brasil]]"
tem_protocolo: true
---

# Passo 2 equaliza o risco entre cenários

> **Resumo:** O Passo 2 define quanto capital cada cenário recebe na carteira global. O critério é igualar a contribuição de volatilidade entre os cenários, para que nenhum regime domine o risco total.

## Explicação Detalhada

Depois de definir os ativos de cada cenário, o método passa a calcular o peso percentual de capital destinado a cada um dos quatro blocos. A lógica é encontrar pesos em que a multiplicação do peso do cenário pela sua volatilidade produza contribuição semelhante de risco para todos. O texto ressalta que o Cenário 2 é uma exceção, pois seu ativo principal, o CDI, tem volatilidade zero e não permite o cálculo matemático de paridade de risco da mesma forma que os demais.

## Aplicação Prática / Protocolo

Usar o Passo 2 para revisar a exposição de carteira aos diferentes regimes macro antes de detalhar os ativos. Sinal de alerta: um cenário com volatilidade muito baixa ou zero pode exigir premissas manuais, e isso precisa ser documentado para evitar falsa precisão matemática.

## Fonte

- [[Cálculo de Pesos para Carteira Paridade de Risco Brasil]]
