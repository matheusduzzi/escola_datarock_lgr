# Pedidos e mensagens da Loja Exemplo

A Loja Exemplo é inventada. Os clientes se chamam "Cliente 0001", "Cliente 0002" e assim por diante. Nenhum dado vem de pessoa ou empresa real.

## `pedidos.csv`

120 pedidos, um por linha.

| Coluna | O que tem |
|---|---|
| `id_pedido` | número do pedido, de 1 a 120 |
| `cliente` | quem comprou, como "Cliente 0143" |
| `produto` | nome do produto |
| `valor` | valor do pedido em reais, com ponto decimal (`850.00`) |
| `status` | `aguardando_pagamento`, `em_separacao`, `enviado`, `entregue` ou `cancelado` |
| `previsao_entrega` | data prevista, no formato `AAAA-MM-DD` |

O pedido 42 vale exatamente 200 reais, o limite do reembolso sem aprovação. Um mesmo cliente pode ter mais de um pedido.

## `mensagens.csv`

59 mensagens de clientes para o atendimento.

| Coluna | O que tem |
|---|---|
| `id_mensagem` | número da mensagem |
| `texto` | o que o cliente escreveu; pode vir vazio, só com espaços, em maiúsculas ou com acento |
| `rota_esperada` | para onde a mensagem deve ir: `pedido`, `troca` ou `humano` |

As aulas dizem quando usam cada arquivo. Não edite os CSVs à mão: as contas das aulas partem deles do jeito que estão.
