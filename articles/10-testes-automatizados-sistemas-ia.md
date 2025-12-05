# Testes Automatizados para Sistemas de IA: Unitários, Integração e "LLM-as-a-Judge"

<div align="center">
  <img src="../img/artigo_10/capa.png" alt="Capa: Testes em Sistemas de IA" width="70%">
</div>

## 1. Contexto e Propósito (Purpose)

"Como eu sei que a mudança no prompt não quebrou tudo?"
Essa é a pergunta de 1 milhão de dólares. Em software tradicional, temos `assert result == expected`. Em IA, o resultado muda a cada execução, e "quase igual" pode ser aceitável ou catastrófico.
Sem testes automatizados, você tem medo de mexer no prompt. Se tem medo de mexer, seu produto estagna.

O propósito deste artigo é mostrar como criar uma **pipeline de testes confiável** para sistemas estocásticos, permitindo refatorar prompts e trocar modelos com segurança.

## 2. Abordagem (Approach)

Vamos dividir a estratégia de testes em três camadas:

1.  **Testes Determinísticos**: Validam a estrutura (JSON schema, não estar vazio).
2.  **Testes Semânticos (LLM-as-a-Judge)**: Usam um LLM forte para avaliar a resposta de um LLM rápido.
3.  **Testes de Regressão**: Garantir que o bot não "desaprendeu" o que já sabia.

## 3. Conceitos Fundamentais

- **LLM-as-a-Judge**: Usar o GPT-4 para dar uma nota (0 a 5) para a resposta do GPT-3.5. É caro, mas escala melhor que humanos.
- **Golden Dataset**: Um conjunto de perguntas e respostas ideais (curado por humanos) que serve como gabarito.
- **Asserts Fuzzy**: Em vez de igualdade exata, verificamos se a resposta _contém_ palavras-chave ou se o _sentimento_ é positivo.

## 4. Mão na Massa: Exemplo Prático

### Cenário: Chatbot de Recomendação de Pratos

Queremos testar se o bot recomenda pratos que realmente existem no cardápio e se é educado.

#### 1. Teste de Estrutura (Pytest Padrão)

```python
def test_recommendation_structure():
    response = bot.ask("Estou com fome de pizza")
    # Garante que retornou um JSON válido
    data = json.loads(response)
    assert "dishes" in data
    assert len(data["dishes"]) > 0
    assert "price" in data["dishes"][0]
```

#### 2. Teste Semântico com LLM-as-a-Judge

Aqui usamos um prompt avaliador para julgar a qualidade.

```python
def evaluate_politeness(bot_response):
    judge_prompt = f"""
    Avalie se a seguinte resposta é educada e prestativa.
    Resposta: "{bot_response}"
    Responda apenas com SIM ou NAO.
    """
    verdict = gpt4.generate(judge_prompt)
    return verdict.strip() == "SIM"

def test_bot_is_polite():
    response = bot.ask("Essa comida é horrível!")
    assert evaluate_politeness(response) is True
```

#### 3. Teste de Alucinação (RAG)

Verificar se o prato sugerido está na lista de documentos recuperados.

```python
def test_no_hallucination():
    query = "Sugira um prato vegano"
    retrieved_docs = retriever.search(query)
    response = bot.ask(query, context=retrieved_docs)

    # Verifica se a resposta cita apenas itens que estão no contexto
    assert check_groundedness(response, retrieved_docs) is True
```

## 5. Métricas, Riscos e Boas Práticas

### Riscos

- **Custo do Teste**: Rodar 1000 testes usando GPT-4 como juiz custa dinheiro. Use modelos menores para testes rápidos e deixe o GPT-4 para a bateria noturna (Nightly Builds).
- **Viés do Juiz**: O GPT-4 tende a preferir respostas verbosas (como ele mesmo gera).

### Boas Práticas

- **Separe Testes de Prompt vs Testes de Código**: Testes de código rodam a cada commit. Testes de prompt (evals) rodam quando o arquivo de prompt muda.
- **Dataset Evolutivo**: Sempre que um usuário reportar um erro, adicione esse caso ao seu Golden Dataset.

## 6. Evidence & Exploration

Ferramentas como **DeepEval**, **Ragas** ou **Promptfoo** facilitam muito essa implementação.
Experimente rodar o `promptfoo` para comparar como o GPT-3.5 e o Claude 3 respondem ao mesmo prompt de recomendação.

## 7. Reflexões Pessoais & Próximos Passos

Testar IA é menos sobre "Passou/Falhou" e mais sobre "A nota média subiu ou desceu?". É um jogo de estatística.
Agora que garantimos a qualidade técnica, precisamos garantir a operação em produção.

No próximo artigo, vamos falar sobre **Básico de MLOps/LLMOps**: como deployar, monitorar e gerenciar o ciclo de vida desses modelos.
