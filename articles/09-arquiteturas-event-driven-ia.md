# Arquiteturas Event-Driven para IA: Desacoplando a inteligência do fluxo crítico

<div align="center">
  <img src="../img/artigo_9/capa.png" alt="Capa: Arquiteturas Event-Driven para IA" width="70%">
</div>

## 1. Contexto e Propósito (Purpose)

Em um app de delivery, o "caminho feliz" (fazer pedido -> pagar -> entregar) não pode parar nunca. Se você insere uma chamada de IA síncrona no meio desse fluxo (ex: "validar se o item do pedido não viola políticas"), você adicionou um ponto de falha de 10 segundos.
Se a OpenAI cair, ninguém pede comida. Isso é inaceitável.

O propósito deste artigo é mostrar como **arquiteturas orientadas a eventos (EDA)** permitem adicionar inteligência ao sistema sem comprometer a disponibilidade do fluxo principal. A IA deve ser um "observador ativo", não um "porteiro bloqueante".

## 2. Abordagem (Approach)

Vamos desenhar uma arquitetura onde eventos de negócio disparam processos de IA em background:

1.  **O Evento**: `OrderDelivered` (Pedido Entregue).
2.  **O Consumidor**: Um worker que escuta esse evento.
3.  **A Ação**: O worker chama o LLM para analisar a avaliação do cliente e gerar tags automáticas.

## 3. Conceitos Fundamentais

- **Desacoplamento Temporal**: O produtor do evento (app) não precisa esperar o consumidor (IA) terminar.
- **Dead Letter Queue (DLQ)**: Para onde vão as mensagens que a IA não conseguiu processar (ex: erro 500 persistente).
- **Idempotência**: Garantir que se o mesmo evento for processado duas vezes, a IA não gere duas respostas duplicadas ou cobre duas vezes.

## 4. Mão na Massa: Exemplo Prático

### Cenário: Análise de Sentimento de Reviews em Tempo Real

O usuário posta uma review. O app salva e retorna "Obrigado!" imediatamente (200 OK).
Nos bastidores, um evento é publicado no Kafka/RabbitMQ.

#### 1. Publicando o Evento (Producer)

```python
# App Principal (API)
def post_review(user_id, restaurant_id, text, rating):
    review = save_to_db(user_id, restaurant_id, text, rating)

    # Dispara e esquece (Fire and Forget)
    event_bus.publish("reviews.created", {
        "review_id": review.id,
        "text": text,
        "timestamp": now()
    })

    return {"status": "received"}
```

#### 2. Consumindo e Processando (Consumer Worker)

```python
# Worker de IA (Processo separado)
@event_bus.subscribe("reviews.created")
def handle_new_review(event):
    review_text = event["text"]

    # Chama o LLM (pode demorar 30s, não importa)
    sentiment = llm.analyze_sentiment(review_text)
    suggested_reply = llm.generate_reply(review_text)

    # Salva o resultado enriquecido
    db.update_review_metadata(event["review_id"], {
        "sentiment": sentiment,
        "ai_reply_draft": suggested_reply
    })

    # Se for muito negativo, dispara outro evento
    if sentiment == "CRITICAL":
        event_bus.publish("reviews.critical_alert", {"id": event["review_id"]})
```

### Diagrama Lógico

`App` -> [Tópico: reviews.created] -> `Worker IA` -> (LLM) -> `DB`
-> [Tópico: reviews.critical] -> `Slack Bot`

## 5. Métricas, Riscos e Boas Práticas

### Riscos

- **Lag de Processamento**: O usuário pode atualizar a página e não ver a resposta da IA ainda. A UI precisa lidar com esse estado "eventual".
- **Custo Descontrolado**: Se um bug no produtor gerar 1 milhão de eventos em loop, seu worker vai chamar a OpenAI 1 milhão de vezes. Implemente **Circuit Breakers de Custo**.

### Boas Práticas

- **Batching**: Em vez de chamar o LLM para cada review, agrupe 10 reviews e mande em um único prompt. Isso economiza tokens de instrução e requests.
- **Observabilidade de Fila**: Monitore o tamanho da fila (`queue_depth`). Se estiver crescendo muito, suba mais workers (HPA).

## 6. Evidence & Exploration

Compare a latência do endpoint `POST /reviews`:

- **Síncrono (com IA)**: 4.5 segundos (P99).
- **Assíncrono (Event-Driven)**: 120 milissegundos (P99).

A experiência do usuário melhora drasticamente, e a IA roda no tempo dela.

## 7. Reflexões Pessoais & Próximos Passos

Event-Driven é a arquitetura nativa da IA Generativa em escala. Tentar forçar LLMs em fluxos síncronos é lutar contra a física do modelo.
Mas como garantimos que essa IA está funcionando corretamente? Como testar um sistema que é assíncrono e não-determinístico?

No próximo artigo, vamos falar sobre **Testes Automatizados para Sistemas de IA**: unitários, integração e avaliação de qualidade.
