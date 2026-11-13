# Meu diagrama do atendimento, com reembolso

## 1. O estado

As chaves que o atendimento já tem, do diagrama da aula:

| Chave | O que guarda | Quem escreve |
|---|---|---|
| `mensagem` | o texto que o cliente mandou | a entrada, pelo `START` |
| `rota` | o assunto: `pedido`, `troca` ou `humano` | `classificar` |
| `consulta` | o que a consulta achou: `achou`, `sem_numero`, `nao_achou` ou `falhou` | `consultar` |
| `tentativas` | quantas vezes o sistema falhou nessa mensagem | `classificar` começa em 0, `consultar` soma 1 a cada falha |
| `pedido` | o pedido que o sistema retornou | `consultar` |
| `resposta` | o texto que vai para o cliente | `responder`, `pedir_numero`, `troca`, `humano` |
| `motivo` | por que a mensagem foi para uma pessoa | `humano` |

Acrescente aqui as chaves do reembolso, com quem escreve cada uma.

## 2. A tabela de transições

Esta é a tabela da aula. Mude o que precisar e acrescente as linhas do reembolso.

| De | Quando | Vai para |
|---|---|---|
| START | sempre | classificar |
| classificar | rota é pedido | consultar |
| classificar | rota é troca | troca |
| classificar | rota é humano | humano |
| classificar | qualquer outra rota | humano |
| consultar | achou o pedido | responder |
| consultar | mensagem sem número | pedir_numero |
| consultar | número não existe | humano |
| consultar | sistema falhou e tentativas < 3 | consultar |
| consultar | sistema falhou 3 vezes | humano |
| responder | sempre | END |
| pedir_numero | sempre | END |
| troca | sempre | END |
| humano | sempre | END |

## 3. O desenho

Cole aqui a foto ou o link do seu desenho.

## 4. Os sete casos

| Caso | Caminho, do START ao END | Onde pausa |
|---|---|---|
| a. reembolso do pedido 42 (200,00) | | |
| b. reembolso do pedido 27 (79,90) | | |
| c. reembolso do pedido 86 (850,00), financeiro responde "aprovado" | | |
| d. reembolso do pedido 86, financeiro responde "deixa eu ver depois" | | |
| e. "Quero meu dinheiro de volta", sem número | | |
| f. reembolso do pedido 999 | | |
| g. reembolso do pedido 84, sistema fora o tempo todo | | |

## 5. As quatro perguntas

| Pergunta | Sim ou não | A linha da tabela que mostra |
|---|---|---|
| Todo nó é alcançado a partir do START? | | |
| De todo nó dá para chegar ao END? | | |
| Toda seta que volta tem contador? | | |
| Toda decisão aberta tem uma saída para o resto? | | |
