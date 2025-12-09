# Monitorando a Qualidade das Respostas: Além do "Thumbs Up/Down"

<div align="center">
  <img src="../img/artigo_12/capa.png" alt="Capa: Monitorando qualidade" width="70%">
</div>

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

### Teste Prático 1: Análise de Padrões de Erro

Ferramentas como **Arize Phoenix** ou **LangSmith** geram gráficos automáticos. Mas você pode fazer manualmente:

```python
import pandas as pd

# Carregue seus logs de feedback
df = pd.read_sql("SELECT * FROM ai_interactions WHERE user_feedback_score < 0", db)

# Agrupe por tópico ou tipo de pergunta
errors_by_topic = df.groupby('topic').agg({
    'id': 'count',
    'user_feedback_score': 'mean'
}).sort_values('id', ascending=False)

print(errors_by_topic)
# Resultado esperado:
#                    id  user_feedback_score
# Restaurant Offers  48  -0.95  <- PROBLEMA CRÍTICO
# Refund Policy      32  -0.72  <- problema médio
# Order Tracking     15  -0.40  <- aceitável
```

**Ação:** Se "Restaurant Offers" tem 48 dislikes, é bug sistemático, não variação aleatória.

### Teste Prático 2: Amostragem Humana Calibrada

Diariamente, selecione aleatoriamente 50 conversas e peça revisão (PM ou QA):

```python
import random

sample = random.sample(df['id'].tolist(), 50)
# Exporta para CSV para revisão humana
review_df = df[df['id'].isin(sample)][['user_id', 'input_text', 'output_text']]
review_df.to_csv('daily_review_sample.csv')

# Após review, salve os scores calibrados
# compare com feedback automático dos usuários
# Encontre divergências (usuário deu like, mas humano achou errado = falso positivo)
```

### Teste Prático 3: Detecção de "Re-prompting"

Se o usuário edita a pergunta 3 vezes seguidas = frustração:

```python
def detect_user_frustration(conversation):
    """Detecta sinais de frustração"""
    edits_in_row = 0
    signals = []

    for msg in conversation:
        if msg['type'] == 'user_edit':
            edits_in_row += 1
            if edits_in_row >= 3:
                signals.append("high_frustration")
                break
        elif msg['type'] == 'ai_response':
            edits_in_row = 0  # reset

    return signals

# Monitore:
frustration_rate = sum(1 for c in conversations if detect_user_frustration(c)) / len(conversations)
# Se > 5%, temos problema

# Debug: quali conversas têm frustração?
problematic = [c for c in conversations if detect_user_frustration(c)]
# Analise os tópicos comuns
```

### Ferramentas Recomendadas

- **Arize Phoenix**: Detecção automática de drift, LLM evals integrados
- **LangSmith**: Observabilidade para LangChain pipelines
- **WhyLabs**: Monitoramento de dados com alertas
- **Custom Solutions**: DataFrame + análise descritiva (não precisa de ferramenta cara para começar)

## 7. Reflexões Pessoais & Próximos Passos

### A Lição: Qualidade é Observável

Qualidade é subjetiva, mas **padrões de erro não são**. Se 30% dos usuários reclamam da mesma coisa, não é "gosto pessoal", é **bug sistemático**.

O segredo é instrumentar desde o início. Um botão simples de 👍/👎 gera dados que, agregados, revelam a verdade.

### Conectando com a Série

Percurso completo:

- ✅ Modelo rodando (Artigo 01)
- ✅ Prompt versionado (Artigo 06)
- ✅ API resiliente (Artigo 07-08)
- ✅ Pipeline de deploy (Artigo 11)
- ✅ Feedback estruturado (Artigo 12)

Agora falta uma coisa crucial: **logging estruturado e observabilidade distribuída** para debugar problemas complexos.

### Próximos Passos

1. **Adicione feedback ao seu app**: Um botão 👍/👎 em cada resposta (1 hora de desenvolvimento).
2. **Registre em banco estruturado**: Crie a tabela SQL acima (30 minutos).
3. **Implement amostragem humana**: 50 conversas/dia para calibração (configurar processo).
4. **Analise padrões**: Semanalmente, rode o pandas script acima para achar bugs.
5. **Leia o Artigo 13**: Vamos falar sobre **Logging e Métricas para GenAI**: como rastrear custo por token, cache hit rate, e correlacionar tudo com observabilidade distribuída.
