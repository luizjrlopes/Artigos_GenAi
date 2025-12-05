# Logging e Métricas para GenAI: O que medir para não falir

![Capa: Logging e Métricas](../img/artigo_13/capa.png)

## 1. Contexto e Propósito (Purpose)

Em sistemas tradicionais, logs são texto ("User logged in"). Em GenAI, logs são dinheiro. Cada token de entrada e saída tem um custo direto. Além disso, a latência não é binária; o "Time to First Token" importa mais que o tempo total.
Se você não tem observabilidade granular sobre _quem_ está gastando _quanto_ e _onde_, sua fatura da OpenAI vai chegar como uma surpresa desagradável no fim do mês.

O propósito deste artigo é definir as **métricas essenciais** para operações de GenAI e como estruturar logs para auditoria e otimização de custos.

## 2. Abordagem (Approach)

Vamos focar em três pilares de observabilidade:

1.  **Métricas de Performance**: Latência, TTFT, Throughput.
2.  **Métricas de Custo**: Token Usage (Prompt vs Completion).
3.  **Rastreabilidade (Tracing)**: Acompanhar o fluxo da requisição através do RAG, VectorDB e LLM.

## 3. Conceitos Fundamentais

- **Token Usage**: A unidade atômica de custo. Prompt tokens são mais baratos que Completion tokens.
- **Cache Hit Rate**: Quantas requisições foram respondidas pelo cache sem bater no LLM (economia de 100% e latência zero).
- **Tracing Distribuído**: Ferramentas como OpenTelemetry que mostram o "waterfall" da requisição (ex: 200ms no Redis -> 500ms no Pinecone -> 5s no GPT-4).

## 4. Mão na Massa: Exemplo Prático

### Instrumentando com OpenTelemetry (Python)

Vamos criar um wrapper que loga automaticamente métricas para o Prometheus/Grafana.

```python
from opentelemetry import trace, metrics
import time

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

token_counter = meter.create_counter("llm_tokens_total")
latency_histogram = meter.create_histogram("llm_latency_seconds")

def call_llm_with_observability(prompt, model="gpt-4"):
    with tracer.start_as_current_span("llm_call") as span:
        start_time = time.time()

        # Chamada real (simulada)
        response = openai.ChatCompletion.create(...)

        duration = time.time() - start_time

        # Extraindo metadados
        usage = response['usage']
        prompt_tokens = usage['prompt_tokens']
        completion_tokens = usage['completion_tokens']

        # Logando métricas
        token_counter.add(prompt_tokens, {"type": "prompt", "model": model})
        token_counter.add(completion_tokens, {"type": "completion", "model": model})
        latency_histogram.record(duration, {"model": model})

        # Adicionando atributos ao Trace para debug
        span.set_attribute("llm.model", model)
        span.set_attribute("llm.prompt_tokens", prompt_tokens)
        span.set_attribute("llm.cost_usd", calculate_cost(usage, model))

        return response
```

### Dashboard Sugerido (Grafana)

1.  **Custo por Hora ($)**: Stacked bar chart por modelo.
2.  **Latência (P95 e P99)**: Line chart.
3.  **Top Usuários Gastões**: Table ordenada por `sum(tokens)`.
4.  **Cache Hit Rate**: Gauge (Alvo > 30%).

## 5. Métricas, Riscos e Boas Práticas

### Riscos

- **Logs Verborrágicos**: Logar o texto completo do prompt/response pode vazar PII (dados pessoais) nos logs. Use máscaras ou logue apenas metadados em produção.
- **Cardinalidade Alta**: Não coloque o `user_id` como label no Prometheus, ou você vai explodir a memória da time-series database.

### Boas Práticas

- **Alertas de Anomalia**: Configure um alerta se o gasto em 1 hora superar $50. Isso pega loops infinitos antes de falir a empresa.
- **Tagging de Features**: Adicione tags como `feature="menu_summary"` ou `feature="support_chat"` para saber qual funcionalidade está custando mais.

## 6. Evidence & Exploration

Instale o **LangFuse** ou **HoneyHive** (ferramentas especializadas em LLM Observability). Elas já dão esses dashboards prontos e permitem clicar num ponto do gráfico e ver o prompt exato que gerou aquele custo.

## 7. Reflexões Pessoais & Próximos Passos

O que não é medido não é gerenciado. Em GenAI, o que não é medido vira prejuízo muito rápido.
Agora que sabemos quanto estamos gastando, a pergunta óbvia é: **como gastar menos?**

No próximo artigo, vamos falar sobre **Custos de IA e Chamadas de Modelo**: estratégias de caching, modelos menores e otimização de prompts para reduzir a fatura.
