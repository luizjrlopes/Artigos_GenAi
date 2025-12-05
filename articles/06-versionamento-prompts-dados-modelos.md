# Versionamento de Prompts, Dados e Modelos: O "Git" da Engenharia de IA

<div align="center">
  <img src="../img/artigo_6/capa.png" alt="Capa: Versionamento em IA" width="70%">
</div>

## 1. Contexto e Propósito (Purpose)

Em engenharia de software tradicional, se o código não mudou, o comportamento do software geralmente não muda. Em GenAI, isso é mentira.
Você pode ter o mesmo código Python rodando, mas se a OpenAI atualizar o modelo, ou se o seu prompt mudar uma vírgula, ou se os dados do seu VectorDB forem atualizados, a resposta final muda.

O propósito deste artigo é abordar o **caos da não-reprodutibilidade**. Em um app de delivery, se um cliente reclama que o chatbot foi rude ontem, você precisa ser capaz de "voltar no tempo" e ver exatamente:

1.  Qual versão do prompt estava rodando?
2.  Qual modelo (e versão) foi usado?
3.  Quais dados de contexto (RAG) foram injetados?

## 2. Abordagem (Approach)

Vamos tratar o versionamento sob três pilares:

1.  **Prompts as Code**: Por que prompts devem viver no Git, não no banco de dados.
2.  **Model Registry**: Gerenciando atualizações de LLMs externos.
3.  **Data Lineage**: Rastreando a origem dos dados do RAG.

## 3. Conceitos Fundamentais

- **Determinismo vs. Estocasticidade**: Softwares tradicionais são determinísticos. LLMs são estocásticos. O versionamento tenta trazer controle sobre essa aleatoriedade.
- **Prompt Registry**: Um sistema ou padrão para buscar prompts por versão (ex: `get_prompt("refund_policy", version="v2.1")`).
- **Drift**: Mudança de comportamento do modelo ao longo do tempo (mesmo mantendo a versão "congelada", provedores podem fazer micro-updates).

## 4. Mão na Massa: Exemplo Prático

### Estrutura de Pastas para "Prompt as Code"

Em vez de hardcoded strings, trate prompts como assets.

```text
/prompts
  /customer-support
    refund-policy.v1.yaml
    refund-policy.v2.yaml
    refund-policy.latest.yaml -> symlink para v2
  /menu-recommendation
    dinner-suggestions.v1.yaml
```

### Exemplo de Arquivo de Prompt (YAML)

```yaml
# refund-policy.v2.yaml
meta:
  id: refund-policy
  version: 2.0
  author: "maria.silva"
  model_config:
    provider: "openai"
    model: "gpt-4-turbo"
    temperature: 0.2

template: |
  Você é um assistente de suporte do iFood.
  Regra de reembolso: Apenas para pedidos com atraso > {{delay_threshold}} minutos.
  Contexto do pedido: {{order_context}}

  Responda ao cliente: {{user_message}}
```

### Implementação Simples de um Loader

```python
import yaml

class PromptLoader:
    def load(self, prompt_id, version="latest"):
        # Lógica para buscar o arquivo YAML correto
        path = f"prompts/{prompt_id}.{version}.yaml"
        with open(path) as f:
            data = yaml.safe_load(f)
        return data

# Uso no código da aplicação
loader = PromptLoader()
prompt_data = loader.load("refund-policy", version="v2")

# Garantia de reprodutibilidade:
log_interaction(
    prompt_id=prompt_data['meta']['id'],
    prompt_version=prompt_data['meta']['version'],
    model=prompt_data['meta']['model_config']['model'],
    input=user_input,
    output=llm_response
)
```

## 5. Métricas, Riscos e Boas Práticas

### Riscos

- **"Shadow Prompts"**: Desenvolvedores alterando prompts diretamente no painel da OpenAI/Azure e esquecendo de commitar no Git.
- **Quebra de Contrato**: A versão v2 do prompt espera uma variável `{{user_age}}` que a v1 não esperava, quebrando o código que chama o prompt.

### Boas Práticas

- **Imutabilidade**: Nunca edite a `v1`. Crie a `v2`.
- **Testes de Regressão**: Antes de promover a `v2` para `latest`, rode uma bateria de avaliações (veremos isso no artigo 10) para garantir que a qualidade não caiu.

## 6. Evidence & Exploration

Ferramentas como **MLflow** ou **LangSmith** já oferecem registries prontos. Mas começar com Git + YAML estruturado resolve 90% dos problemas iniciais de times pequenos e médios.

Experimente: Tente reproduzir um bug de 3 dias atrás. Se você não sabe qual prompt estava rodando, você tem um problema de engenharia, não de IA.

## 7. Reflexões Pessoais & Próximos Passos

Versionamento é a base da sanidade. Sem ele, você não faz ciência, faz alquimia.
Agora que temos controle sobre O QUE estamos enviando para o modelo, precisamos falar sobre **como desenhar a interface de comunicação** entre nossos sistemas e esses modelos.

No próximo artigo, vamos explorar o **Design de APIs para GenAI** (streaming, async, webhooks).
