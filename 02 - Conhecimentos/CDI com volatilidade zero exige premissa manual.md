---
tipo: conhecimento
categoria: "Construção de Carteira"
tags:
  - cdi
  - volatilidade-zero
  - premissa
  - cenario-2
fonte: "Cálculo de Pesos para Carteira Paridade de Risco Brasil"
pdf: "[[Cálculo de Pesos para Carteira Paridade de Risco Brasil.pdf]]"
nota_fonte: "[[Cálculo de Pesos para Carteira Paridade de Risco Brasil]]"
tem_protocolo: true
---

# CDI com volatilidade zero exige premissa manual

> **Resumo:** O CDI não pode ser tratado como os demais cenários no cálculo de paridade de risco porque sua volatilidade é zero. Por isso, o material fixa manualmente 25% da carteira para o Cenário 2.

## Explicação Detalhada

O trecho explica que, como o CDI tem volatilidade zero, não é possível equalizar sua contribuição de risco matematicamente com a dos outros cenários. Para contornar isso, o autor adota uma premissa manual e trava a alocação do Cenário 2 em 25%, interpretando esse número como uma divisão neutra de 1/4 do portfólio entre os quatro cenários. Esse é um ponto central do método, pois insere uma decisão discricionária em meio ao cálculo de paridade.

## Aplicação Prática / Protocolo

Registrar explicitamente essa premissa ao montar a carteira e reavaliá-la se o papel do CDI na estratégia mudar. Risco: tratar a alocação travada como resultado “científico” quando, na prática, ela é uma convenção para lidar com um ativo sem volatilidade.

## Fonte

- [[Cálculo de Pesos para Carteira Paridade de Risco Brasil]]
