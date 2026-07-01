# Status de Pedidos e Tratamento de Divergências

## Status do Pedido de Compra (KingStar)
- **PENDENTE**: PO emitido, aguardando recebimento.
- **RECEBIDO**: mercadoria recebida e conferida.
- **CANCELADO**: PO cancelado (erro, desistência, problema com fornecedor).

## Divergências (PCL — Ponto de Controle Logístico)
Quando a contagem física diverge da NF, o item entra em análise de PCL:
- **Falta**: quantidade física menor que a nota.
- **Sobra**: quantidade física maior que a nota.
- **Avaria**: produto danificado.
A decisão pode ser **aprovar** (aceitar a diferença) ou **rejeitar** (devolver/recusar).

## Sinais de alerta para o gestor de compras
- Pedidos pendentes com muitos dias em aberto.
- Alta taxa de cancelamento concentrada em um fornecedor.
- Recorrência de divergências do mesmo SKU ou fornecedor.
