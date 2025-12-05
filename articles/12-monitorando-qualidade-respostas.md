# Monitorando a Qualidade das Respostas: Além do "Thumbs Up/Down"

![Capa: Monitorando qualidade](../img/artigo_12/capa.png)

## 1. Contexto e Propósito (Purpose)

Seu dashboard no Grafana está todo verde: latência baixa, zero erros 500, CPU sobrando. Mas no Twitter, os usuários estão reclamando que o chatbot do seu app de delivery é "burro" e "não resolve nada".
Monitoramento de infraestrutura (APM) não captura **qualidade semântica**. O servidor pode responder com sucesso (200 OK) uma alucinação completa.

O propósito deste artigo é mostrar como instrumentar sua aplicação para medir se a IA está sendo _útil_, não apenas _rápida_.

## 2. Abordagem (Approach)

Vamos explorar três camadas de monitoramento de qualidade:

1.  **Feedback Explícito**: O clássico botão de "Joinha" (👍/👎).
2.  **Feedback Implícito**: Sinais comportamentais (o usuário copiou o texto? O usuário refez a pergunta?).
3.  **Avaliação Automatizada em Batch**: Usar um LLM mais forte para auditar amostras de conversas diariamente.

## 3. Conceitos Fundamentais

- **Human-in-the-loop (HITL)**: Quando humanos revisam uma amostra das interações para rotular a qualidade (caro, mas necessário para criar o "Golden Set").
- **Sentiment Drift**: A mudança gradual no humor dos usuários ao longo do tempo.
- **Refusal Rate**: A porcentagem de vezes que o modelo se recusa a responder (por filtros de segurança ou falta de contexto).

## 4. Mão na Massa: Exemplo Prático

### 1. Modelagem de Dados para Logs de IA

Não jogue logs de IA no `stdout` misturado com logs de sistema. Crie uma tabela ou índice estruturado.

```sql
CREATE TABLE ai_interactions (
    id UUID PRIMARY KEY,
    user_id UUID,
    prompt_version VARCHAR(50),
    input_text TEXT,
    output_text TEXT,
    latency_ms INT,
    user_feedback_score INT, -- 1 (like) ou -1 (dislike)
    user_feedback_text TEXT, -- "Resposta errada!"
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 2. Endpoint de Feedback

O frontend deve chamar isso assim que o usuário interagir.

```python
@app.post("/interactions/{id}/feedback")
def submit_feedback(id: UUID, score: int, comment: str = None):
    # Salva o feedback
    db.update_interaction(id, score, comment)

    # Se for negativo, manda para análise imediata
    if score < 0:
        event_bus.publish("ai.feedback.negative", {"id": id})

    return {"status": "recorded"}
```

### 3. Worker de Análise de Causa Raiz

Quando um feedback negativo chega, usamos o GPT-4 para tentar entender o porquê (já que o usuário raramente explica).

```python
@event_bus.subscribe("ai.feedback.negative")
def analyze_failure(event):
    interaction = db.get_interaction(event["id"])

    analysis_prompt = f"""
    O usuário deu dislike nesta interação.
    Usuário: {interaction.input_text}
    Bot: {interaction.output_text}

    Analise o motivo provável:
    1. Alucinação (Fato incorreto)
    2. Recusa desnecessária
    3. Tom rude
    4. Falta de contexto

    Responda com JSON.
    """

    reason = gpt4.generate(analysis_prompt)
    db.save_analysis(event["id"], reason)
```

## 5. Métricas, Riscos e Boas Práticas

### Riscos

- **Viés de Seleção**: Apenas usuários muito felizes ou muito irritados dão feedback. A "maioria silenciosa" é ignorada.
- **Gaming the System**: Se você bonifica o time por "Thumbs Up", eles podem criar prompts que imploram por likes ("Se ajudei, dê um joinha!"), o que piora a UX.

### Boas Práticas

- **Amostragem Aleatória**: Diariamente, pegue 50 conversas aleatórias e peça para um humano (PM ou QA) ler. Isso calibra sua percepção da realidade.
- **Monitore "Re-prompting"**: Se o usuário edita a pergunta 3 vezes seguidas, é sinal de que o modelo não está entendendo.

## 6. Evidence & Exploration

Ferramentas como **Arize Phoenix** ou **LangSmith** geram gráficos de "Latência vs Tamanho do Prompt" e "Taxa de Erro por Tópico".
Tente clusterizar as conversas com feedback negativo. Você vai descobrir padrões (ex: "O bot sempre erra quando perguntam sobre vale-refeição").

## 7. Reflexões Pessoais & Próximos Passos

Qualidade é subjetiva, mas padrões de erro não são. Se 30% dos usuários reclamam da mesma coisa, não é "gosto pessoal", é bug.
Agora que estamos monitorando, vamos ver como guardar esses dados de forma eficiente.

No próximo artigo, vamos falar sobre **Logging e Métricas Específicas para GenAI**: custo por token, cache hit rate e rastreabilidade distribuída.
