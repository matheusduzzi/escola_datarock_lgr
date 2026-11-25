# Meu contrato de persistência

O contrato do atendimento, como ficou na aula. Mude as partes que o reembolso e o tamanho de roupa pedem, e depois preencha os oito casos.

## 1. A conversa

O servidor cria o `thread_id` quando a conversa abre, com um código aleatório. O app não escolhe, e o código não leva o nome do cliente. Uma conversa tem um dono só.

## 2. Quem está falando

O cliente vem do login, em toda mensagem, e entra no `invoke` pelo contexto. Ele não fica no estado salvo. O texto da mensagem e o modelo não mudam quem é o cliente.

## 3. O que fica salvo

As mensagens da conversa, no checkpointer. Em produção, banco durável (`PostgresSaver`); o `InMemorySaver` só em teste. A conversa fica 90 dias depois da última mensagem e sai com `delete_thread`. A tabela de donos fica no mesmo banco e sai junto. Só a equipe de sistemas acessa o banco.

## 4. Quem pode abrir

A porta roda antes do `invoke`: o dono da conversa precisa ser o cliente do login. Se não for, ou se a conversa não existe, ela responde "Não achei essa conversa na sua conta" e abre uma conversa nova. Dentro da conversa, a ferramenta continua com a regra da aula 04: o pedido só aparece para o dono.

## 5. Os oito casos

| Caso | Quem decide | O que acontece | Linha do contrato |
|---|---|---|---|
| a | | | |
| b | | | |
| c | | | |
| d | | | |
| e | | | |
| f | | | |
| g | | | |
| h | | | |
