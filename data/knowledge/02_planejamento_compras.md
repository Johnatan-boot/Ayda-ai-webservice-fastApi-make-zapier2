# Planejamento e Compras

## Conceitos centrais
- **Ponto de pedido (reorder point)**: nível de estoque que dispara nova compra.
  Fórmula: `PP = (demanda média diária × lead time) + estoque de segurança`.
- **Estoque de segurança**: colchão para absorver variações de demanda e atrasos.
- **Lote econômico de compra (EOQ)**: quantidade que minimiza custo total
  (pedido + manutenção). `EOQ = raiz(2 × D × S / H)`, onde D=demanda anual,
  S=custo por pedido, H=custo de manutenção por unidade/ano.
- **Curva ABC**: classifica itens por relevância (A: ~80% do valor, poucos itens;
  C: muitos itens, baixo valor). Compras prioriza A.

## Ciclo do Pedido de Compra (PO)
1. Necessidade identificada (planejamento/ponto de pedido).
2. Cotação e seleção de fornecedor (preço, prazo, qualidade, OTIF histórico).
3. Emissão do PO (com SKU, quantidade, preço, prazo de entrega).
4. Acompanhamento (follow-up) até o recebimento.
5. Fechamento e avaliação de desempenho do fornecedor.

## Boas práticas para gestores
- Monitorar pedidos PENDENTES há muito tempo: risco de ruptura.
- Acompanhar a taxa de cancelamento: sinaliza problema de fornecedor ou cadastro.
- Reduzir lead time negociando janelas fixas de entrega.
- Consolidar compras por fornecedor para ganhar escala e frete.
