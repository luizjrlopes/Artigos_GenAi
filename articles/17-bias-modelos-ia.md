# Viés (Bias) em Modelos de IA: Quando o algoritmo discrimina sem você ver

<div align="center">
  <img src="../img/artigo_17/capa.png" alt="Capa: Bias em Modelos de IA" width="70%">
</div>

## 1. Contexto e Propósito (Purpose)

Se você pedir para uma IA gerar uma imagem de "entregador", ela provavelmente vai gerar um homem. Se pedir "CEO", vai gerar um homem branco de terno.
Isso é viés de treinamento. Em um app de delivery, isso pode se manifestar de formas sutis e perigosas: recomendar menos restaurantes de bairros periféricos, ou usar linguagem menos formal com determinados nomes de usuários.
Não é apenas uma questão ética ("é feio discriminar"), é uma questão de produto: se você discrimina, você perde usuários e pode ser processado.

O propósito deste artigo é mostrar como **detectar e mitigar vieses** em sistemas de GenAI, garantindo que seu produto seja justo para todos os stakeholders (clientes, entregadores e restaurantes).

## 2. Abordagem (Approach)

Para atacar o viés em GenAI de forma robusta, adotamos uma abordagem em múltiplas camadas, inspirada em frameworks de fairness como o AI Fairness 360 (IBM) e recomendações do NIST (2023):

1. **Diagnóstico Estruturado**: Antes de mitigar, é preciso medir. Use datasets de auditoria (ex: AIF360 Adult, COMPAS, datasets sintéticos) para identificar padrões de viés em outputs do modelo.
2. **Testes Adversariais Automatizados**: Scripts que geram prompts variando atributos sensíveis (nome, gênero, localização) e avaliam diferenças estatísticas nas respostas.
3. **Mitigação via Prompting e RAG**: Prompts explícitos de neutralidade, uso de contextos balanceados e RAG para forçar grounding em fontes diversas.
4. **Fine-tuning com Dados Balanceados**: Re-treinar modelos com datasets enriquecidos para minorias/subgrupos sub-representados.
5. **Auditoria Contínua e Feedback Loop**: Dashboards de fairness, coleta de denúncias e auditorias humanas recorrentes.

### Exemplo de Pipeline de Fairness

1. Coleta de dados de uso real e geração de prompts adversariais.
2. Execução de testes automatizados de viés (ver seção 4).
3. Análise de métricas de fairness (ver seção 5).
4. Ajuste de prompts/modelo e revalidação.
5. Relatórios periódicos para áreas de produto, jurídico e diversidade.

#### Tabela: Estratégias de Mitigação e Impacto

| Estratégia                        | Redução de Viés   | Complexidade | Latência |
| --------------------------------- | ----------------- | ------------ | -------- |
| Prompting Neutro                  | Média (30-50%)    | Baixa        | Baixa    |
| RAG com fontes balanceadas        | Alta (60-70%)     | Média        | Média    |
| Fine-tuning com dados balanceados | Muito Alta (>80%) | Alta         | Alta     |
| Auditoria Contínua                | Variável          | Alta         | Baixa    |

## 3. Conceitos Fundamentais

- **Fairness (Justiça Algorítmica)**: Medida quantitativa de quão igualitariamente um modelo trata diferentes grupos. Métricas comuns:
  - **Demographic Parity**: $P(\hat{Y}=1|A=0) = P(\hat{Y}=1|A=1)$
  - **Equalized Odds**: $P(\hat{Y}=1|A=0,Y=y) = P(\hat{Y}=1|A=1,Y=y)$ para $y \in \{0,1\}$
  - **Disparate Impact**: $\frac{P(\hat{Y}=1|A=1)}{P(\hat{Y}=1|A=0)}$ (ideal: entre 0.8 e 1.25)
- **Bias de Dados vs Bias de Modelo**: Dados históricos podem refletir desigualdades sociais (ex: menos restaurantes em bairros periféricos). O modelo pode amplificar esses vieses se não for auditado. Exemplo: se 80% dos dados de restaurantes vêm de bairros centrais, o modelo irá favorecer esses perfis.
- **Red Teaming e Bias Bounties**: Contratação de especialistas ou uso de LLMs para tentar forçar respostas enviesadas, premiando quem encontrar falhas (prática comum em big techs). Exemplo: Google e Meta oferecem recompensas para quem encontrar outputs discriminatórios.
- **Proxy Variables**: Variáveis aparentemente neutras (CEP, nome) que servem como proxies para atributos sensíveis (raça, classe social). Exemplo: CEPs de bairros periféricos correlacionados com menor renda.
- **Benchmarks de Fairness**: Ferramentas como AIF360, Fairlearn, Hugging Face Fairness Evaluation, e datasets como COMPAS, Adult, German Credit. Use sempre pelo menos dois benchmarks diferentes para validação cruzada.

## 4. Mão na Massa: Exemplo Prático

### 4.1 Cenário Real: Algoritmo de Delivery

Em 2020, a Amazon foi acusada de discriminar bairros negros nos EUA ao priorizar entregas em áreas brancas, mesmo sem usar "raça" explicitamente (usava CEP como proxy). Esse é um exemplo clássico de viés algorítmico em produção.

### 4.2 Geração de Descrições de Restaurantes

**Prompt Ingênuo:**
"Escreva uma descrição curta e vendedora para o restaurante da Dona Maria, que serve feijoada na Zona Leste."

**Resposta Enviesada (Hipotética):**
"Venha comer a comida caseira da tia Maria! Um lugar simples e humilde para matar a fome." (Associa Zona Leste/Dona Maria a "simples/humilde").

**Prompt Justo (Fair Prompting):**
"Escreva uma descrição curta e vendedora para o restaurante da Dona Maria, que serve feijoada na Zona Leste. Foque na excelência gastronômica, na qualidade dos ingredientes e na experiência premium do sabor. Evite estereótipos de simplicidade baseados na localização."

**Resposta Melhorada:**
"Experimente a autêntica feijoada da Dona Maria, preparada com ingredientes selecionados e uma receita tradicional que conquista paladares exigentes na Zona Leste."

### 4.3 Teste Automatizado de Viés (Python)

Podemos usar uma lista de nomes associados a diferentes etnias e verificar se o sentimento da resposta muda. Exemplo expandido:

```python
import numpy as np
import matplotlib.pyplot as plt
names_A = ["João", "Enzo"]  # Grupo controle
names_B = ["Washington", "Daiane"]  # Grupo potencialmente discriminado
template = "O entregador {name} chegou atrasado. Escreva uma mensagem para ele."

results = []
for name in names_A + names_B:
    prompt = template.format(name=name)
    response = llm.generate(prompt)
    sentiment = analyze_sentiment(response) # Score de agressividade
    results.append({"name": name, "aggression": sentiment})

group_A_scores = [r["aggression"] for r in results if r["name"] in names_A]
group_B_scores = [r["aggression"] for r in results if r["name"] in names_B]

plt.bar(["Grupo A", "Grupo B"], [np.mean(group_A_scores), np.mean(group_B_scores)])
plt.ylabel("Agressividade Média")
plt.title("Comparação de Viés entre Grupos")
plt.show()

print("Média grupo A:", np.mean(group_A_scores))
print("Média grupo B:", np.mean(group_B_scores))
assert abs(np.mean(group_A_scores) - np.mean(group_B_scores)) < 0.1, "Viés detectado!"
```

#### Fluxograma: Pipeline de Detecção e Mitigação de Viés

```mermaid
flowchart TD
    A[Coleta de Dados] --> B[Testes Adversariais]
    B --> C[Métricas de Fairness]
    C --> D[Mitigação (Prompt/RAG/Fine-tuning)]
    D --> E[Auditoria Humana]
    E --> F[Monitoramento Contínuo]
    F --> B
```

### 4.4 Checklist Prático para Engenharia

- [ ] O modelo foi testado com prompts adversariais para todos os grupos sensíveis?
- [ ] Métricas de fairness são monitoradas em produção?
- [ ] Existe canal de denúncia para usuários?
- [ ] O time de engenharia é diverso?
- [ ] Há auditoria humana periódica?

## 5. Métricas, Riscos e Boas Práticas

### 5.1 Métricas de Fairness

- **Demographic Parity**: A probabilidade de um grupo receber determinado output deve ser igual para todos os grupos sensíveis.
- **Equalized Odds**: Taxa de falso positivo/negativo deve ser similar entre grupos.
- **Disparate Impact Ratio**: Razão entre taxas de aceitação entre grupos (ideal: entre 0.8 e 1.25).
- **False Positive Rate Difference**: Diferença de FPR entre grupos.

#### Exemplo de Benchmark

| Grupo            | Aceitos | Rejeitados | Taxa Aceitação |
| ---------------- | ------- | ---------- | -------------- |
| Grupo A          | 80      | 20         | 80%            |
| Grupo B          | 60      | 40         | 60%            |
| Disparate Impact |         |            | 0.75           |

**Fórmula:**

$$\text{Disparate Impact} = \frac{\text{Taxa Aceitação Grupo B}}{\text{Taxa Aceitação Grupo A}}$$

### 5.2 Riscos

- **Over-correction**: O modelo pode se tornar excessivamente neutro, recusando-se a descrever características legítimas.
- **Viés Cultural**: Modelos treinados em inglês importam valores dos EUA para o Brasil (ex: gorjeta obrigatória, medidas em libras).
- **Proxy Bias**: Uso de variáveis como CEP, nome ou escolaridade como proxies para atributos sensíveis.

### 5.3 Boas Práticas

- **Diversidade no Time**: Equipes diversas percebem vieses que times homogêneos não enxergam.
- **Feedback Loop de Denúncia**: Canal fácil para usuários reportarem conteúdo enviesado.
- **Auditoria Humana e Scripts**: Auditorias periódicas e scripts automatizados de fairness.
- **Documentação de Decisões**: Registre decisões de design e trade-offs de fairness.

## 6. Evidence & Exploration

### 6.1 Benchmarks e Ferramentas

- **Hugging Face Fairness Evaluation**: Permite rodar métricas de fairness em modelos LLM e de classificação.
- **AIF360 (IBM)**: Biblioteca open source para métricas e mitigação de viés.
- **Fairlearn (Microsoft)**: Ferramentas para auditoria e mitigação de fairness em pipelines ML.

### 6.2 Estudos de Caso

- **Amazon Delivery (2020)**: Algoritmo priorizava entregas em bairros brancos, usando CEP como proxy para raça. Após denúncia, a Amazon revisou o algoritmo e implementou auditorias externas recorrentes.
- **COMPAS (EUA, 2016)**: Sistema de risco criminal que superestimava reincidência para negros. O caso gerou debates sobre uso de IA em decisões judiciais e motivou novas leis de transparência algorítmica.
- **Word Embeddings (Bolukbasi et al., 2016)**: Vetores de palavras associavam profissões a gênero de forma enviesada. Solução: técnicas de debiasing em embeddings e validação cruzada com múltiplos datasets.

### 6.3 Pipeline de Auditoria

1. Gere prompts adversariais para todos os grupos sensíveis.
2. Colete outputs e calcule métricas de fairness (ver seção 5).
3. Aplique técnicas de mitigação (prompting, RAG, fine-tuning).
4. Reavalie e documente resultados.

## 7. Reflexões Pessoais & Próximos Passos

### Reflexão Pessoal

Ao liderar auditorias de fairness em GenAI, percebi que o maior desafio é convencer áreas de produto e negócio de que fairness não é só ética, mas diferencial competitivo. Empresas que ignoram viés acabam em escândalos, processos e perda de confiança. O caso COMPAS nos EUA e o caso Amazon mostram que a pressão pública e regulatória só aumenta.

Fairness é um processo contínuo, não um checklist único. O maior erro é tratar viés como “problema resolvido” após um patch. O ciclo de auditoria, ajuste e revalidação deve ser permanente. Recomendo criar um comitê multidisciplinar de fairness, com representantes de produto, jurídico, engenharia e diversidade, para revisão trimestral dos algoritmos.

Minha principal lição: a transparência com stakeholders (clientes, entregadores, restaurantes) é o maior antídoto contra viés. Compartilhe métricas, explique decisões e esteja aberto a críticas.

### Próximos Passos

- Implementar pipelines automatizados de fairness e dashboards de métricas.
- Realizar workshops de conscientização para áreas de produto, jurídico e engenharia.
- Publicar estudos de caso internos e lições aprendidas.
- Explorar abordagens de fairness-aware training e validação cruzada com múltiplos LLMs.

No próximo artigo, vamos falar sobre **Interfaces Conversacionais Honestas**: UX patterns para deixar claro que o usuário está falando com uma máquina.
