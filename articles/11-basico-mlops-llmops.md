# Básico de MLOps e LLMOps: Tirando a IA do Jupyter Notebook e levando para a vida real

<div align="center">
  <img src="../img/artigo_11/capa.png" alt="Capa: MLOps e LLMOps" width="70%">
</div>

## 1. Contexto e Propósito (Purpose)

Existe um abismo gigante entre "funciona no meu notebook" e "funciona em produção com 1 milhão de usuários".
Cientistas de Dados são ótimos em criar modelos, mas muitas vezes não sabem como empacotar, versionar e escalar isso. Engenheiros de Software sabem escalar, mas não entendem as idiossincrasias de modelos probabilísticos.

O propósito deste artigo é apresentar o **LLMOps** (Large Language Model Operations) como a ponte necessária para operacionalizar GenAI em apps de delivery, garantindo que atualizações de modelo não quebrem o checkout.

## 2. Abordagem (Approach)

Vamos focar no ciclo de vida operacional:

1.  **Deploy**: Como servir o modelo (API Gateway, Containers).
2.  **Monitoramento**: O que olhar além de CPU e Memória.
3.  **Governança**: Quem aprovou esse prompt que está xingando o cliente?

## 3. Conceitos Fundamentais

- **Model Registry**: O "Docker Hub" dos modelos. Onde você guarda a versão `v1.2` do seu Fine-Tuning.
- **Training-Serving Skew**: Quando o ambiente de treino é diferente do de produção (ex: dados limpos no treino, dados sujos na produção), causando performance ruim.
- **Feedback Loop**: O mecanismo para pegar o que o usuário fez com a resposta da IA e usar isso para melhorar a próxima versão.

## 4. Mão na Massa: Exemplo Prático

### Pipeline de CI/CD para Prompts (GitOps)

Não precisamos de ferramentas complexas como Kubeflow para começar. O GitHub Actions já resolve 80%.

#### 1. O Repositório

```text
/prompts
  recommendation.yaml
/tests
  test_recommendation.py
```

#### 2. O Workflow (GitHub Actions)

```yaml
name: LLMOps Pipeline

on:
  push:
    paths:
      - "prompts/**"

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Dependencies
        run: pip install pytest openai

      - name: Run Semantic Tests (LLM-as-a-Judge)
        run: pytest tests/ --junitxml=report.xml
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: Deploy to Staging
        if: success()
        run: python scripts/deploy_prompt.py --env staging
```

### Deploy Blue/Green para Modelos

Se você fez um Fine-Tuning do Llama-3, não troque o modelo de uma vez.

1.  Suba o **Modelo B (Green)** ao lado do **Modelo A (Blue)**.
2.  Mande 1% do tráfego para o B.
3.  Monitore erros e latência.
4.  Se ok, aumente para 10%, 50%, 100%.
5.  Desligue o A.

## 5. Métricas, Riscos e Boas Práticas

### Riscos

- **Drift de Conceito**: O comportamento do usuário muda (ex: na pandemia, o padrão de pedidos mudou totalmente). Seu modelo antigo vai errar tudo.
- **Custo de Infra**: GPUs são caras. Deixar instâncias ociosas é queimar dinheiro. Use **Auto-scaling** baseado em fila, não em CPU.

### Boas Práticas

- **Tags e Metadados**: Todo deploy deve ter tags: `commit_sha`, `author`, `model_version`.
- **Rollback Automático**: Se a taxa de erro subir > 1% após o deploy, o sistema deve voltar para a versão anterior sozinho.

## 6. Evidence & Exploration

### Teste Prático 1: CI/CD para Prompts

Implemente o GitHub Actions acima e faça um teste:

```bash
# 1. Altere o prompt
git add prompts/recommendation.yaml
git commit -m "Teste: mais detalhado"
git push

# 2. GitHub Actions:
#    - Instala dependências
#    - Roda pytest (LLM-as-a-Judge)
#    - Se passar, faz deploy para staging
#    - Se falhar, bloqueia e notifica no Slack

# 3. Resultado: Nenhuma versão quebrada entra em produção
```

### Teste Prático 2: Blue/Green Deployment

Você treinou uma versão fine-tuned do Llama-3. Como rodar os dois modelos em paralelo?

```python
# Histórico de versões no Model Registry
models = {
    "blue": "/models/recommendation.v1",  # modelo antigo
    "green": "/models/recommendation.v2", # modelo novo
}

# Roteamento gradual
if user.id % 100 < 1:  # 1% dos usuários
    model_version = "green"
else:
    model_version = "blue"

response = models[model_version].generate(prompt)
```

**Métricas a monitorar:**

- Latência: Green é mais lento que Blue?
- Taxa de erro: Green tem mais erros?
- Custo: Green é mais caro (mais tokens)?

Se tudo bem após 24h em 1% do tráfego, suba para 10%, depois 50%, depois 100%.

### Teste Prático 3: Feedback Loop

Dentro de 1 dia de deployment:

1. Pegue 100 conversas com score < 0 (dislike)
2. Analise os padrões
3. Itere no prompt/modelo
4. Submeta a próxima versão

**Exemplo de padrão encontrado:**

- "30% dos dislikes são sobre restaurantes fechados não sendo mencionados como opção."
- Ação: Adicione contexto de horário de funcionamento ao prompt

### Ferramentas Recomendadas

- **MLflow**: Registry centralizado, fácil deploy
- **Weights & Biases**: Visualização linda de experimentos
- **vLLM**: Serve modelos open source com cache de prompts (até 20x mais rápido)
- **Kubeflow**: Se você tem K8s e precisa de orquestração complexa

## 7. Reflexões Pessoais & Próximos Passos

### A Lição: "Just Push It" Não Funciona para IA

LLMOps transforma "mágica" em **engenharia confiável**. Sem isso:

- Você implanta um novo modelo e quebra a produção
- Ninguém sabe qual versão está rodando onde
- Rollback é uma aula de "O que deu errado?"

Com LLMOps:

- Cada versão é auditável
- Blue/Green minimiza risco
- Feedback loop acelera iteração

Pense em LLMOps como a infraestrutura que permite **confiança em mudança**.

### Conectando com a Série

Agora temos:

- ✅ Prompts versionados (Artigo 06)
- ✅ APIs resilientes (Artigo 07-08)
- ✅ Arquitetura escalável (Artigo 09-10)
- ✅ Pipeline de deploy confiável (Artigo 11)

Mas como saber se o modelo que deployou está realmente melhor? Não é só latência. É **qualidade da resposta**.

### Próximos Passos

1. **Configure um Model Registry**: MLflow local (5 minutos de setup).
2. **Implemente CI/CD para prompts**: GitHub Actions (30 minutos).
3. **Teste Blue/Green**: Com um modelo dummy (1 hora).
4. **Meça tudo**: Latência, erro, custo, satisfação do usuário.
5. **Leia o Artigo 12**: Vamos falar sobre **Monitorando Qualidade das Respostas**: porque código verde no Grafana não significa que o bot está falando a verdade.
