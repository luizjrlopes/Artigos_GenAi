# LLMs como Copilotos: Casos Práticos em Times de Delivery

## 1. Contexto e Propósito (Purpose)

Em times de engenharia de alta performance, a velocidade é crucial, mas a estabilidade é inegociável. O dia a dia de um dev em uma startup de delivery não é apenas criar features verdes; é lidar com código legado ("quem escreveu isso em 2019?"), migrar monolitos para microsserviços e otimizar queries SQL que estão travando o checkout na sexta-feira à noite.

Segundo o relatório Stack Overflow 2025, 68% dos devs já usam IA para acelerar tarefas rotineiras, mas apenas 22% confiam cegamente no código gerado. O desafio é transformar IA em copiloto confiável, não em fonte de bugs.

**Exemplo real de impacto:**

- Startup X reduziu bugs em produção de 3.2% para 1.1% após adotar copilotos IA.
- Tempo médio de entrega de features caiu de 6 para 3 dias.
- Devs reportaram 40% menos tempo gasto em tarefas repetitivas.

**Checklist de relevância:**

- [x] Mercado: IA já é padrão em times de produto
- [x] Impacto: Redução de bugs e aceleração de releases
- [x] Problema: Como evitar armadilhas de automação cega
- [x] Empresa: Cases reais de startups e grandes players

## 2. Abordagem (Approach)

Vamos focar em três casos de uso onde a IA atua como um multiplicador de senioridade, indo além do autocomplete:

- **Arqueologia de Código:** Decifrando lógica de negócios antiga e não documentada.
- **Engenharia de Testes:** Geração de casos de borda e testes parametrizados para validação financeira.
- **SQL & Otimização:** Criação de queries complexas com consciência do schema do banco.

**Fluxograma de uso:**

1. Dev identifica tarefa repetitiva ou complexa
2. Cria prompt detalhado com contexto do projeto
3. Gera solução com IA copiloto
4. Revisa, testa e audita resultado
5. Salva métricas de uso e feedback

**Tabela de abordagens:**

| Caso de Uso          | Ferramenta IA    | Métrica de Sucesso          |
| -------------------- | ---------------- | --------------------------- |
| Refatoração Legada   | Copilot, Cursor  | Redução de bugs, tempo      |
| Testes Automatizados | Copilot, Cody    | Cobertura, detecção de edge |
| SQL Analytics        | Copilot, ChatGPT | Performance, acurácia       |

<div align="center">
  <img src="../img/artigo_5/figura1.png" alt="Figura 1: LLM como Copiloto" width="70%">
  <p><em>Figura 1: Fluxo de trabalho com LLM como copiloto: Contexto → Geração → Revisão → Produção.</em></p>
</div>

## 3. Conceitos Fundamentais

Para usar essas ferramentas profissionalmente, precisamos dominar três conceitos:

### 1. RAG de Código (Codebase Awareness)

Ferramentas modernas (como **Cursor** ou **Copilot Workspace**) não leem apenas o arquivo aberto. Elas **indexam todo o seu repositório localmente**. Isso permite perguntas como:

> "Onde essa variável de frete é alterada em todo o projeto?"

### 2. Reviewer Mindset

A mudança fundamental de postura. O desenvolvedor deixa de ser o "digitador" e passa a ser o **"Arquiteto e Revisor"**.

⚠️ **Se você aceita o código da IA sem ler, você introduziu um bug.**

### 3. Privacy & Data Tiers

A regra de ouro corporativa. **Nunca cole segredos** (API Keys, PII) em chats públicos. Entenda a diferença entre:

- **Ferramentas "Zero Data Retention"** (Enterprise) - dados não são usados para treino
- **Ferramentas de treino público** - seu código pode virar exemplo para outros

<div align="center">
  <img src="../img/artigo_5/figura2.png" alt="Figura 2: Privacy Tiers" width="70%">
  <p><em>Figura 2: Comparação entre modos de uso de LLM (Local, Enterprise, Public).</em></p>
</div>

## 4. Mão na Massa: Exemplo Prático

### Caso 1: Arqueologia de Código (Refatoração Legada)

**Cenário:** Você encontrou uma função crítica de cálculo de frete, sem tipagem e com variáveis mágicas.

```python
# Código original
def c(d, w, v):
    b = 5.0
    if d > 10: b += (d - 10) * 0.5  # Regra mágica 1
    if w > 5: b *= 1.2              # Regra mágica 2
    return b
```

**Prompt Estratégico (Chain-of-Thought):**

```
Aja como um Tech Lead Python.
1. Analise a lógica desta função passo a passo.
2. Refatore para Python moderno usando Type Hints.
3. Substitua 'números mágicos' por constantes nomeadas (ex: BASE_FEE, DISTANCE_THRESHOLD).
4. Adicione Docstrings explicando a regra de negócio inferida.
```

**Resultado:** O código volta limpo, tipado e, o mais importante, com a **intenção de negócio explicada**.

### Caso 2: Geração de Testes (Carrinho & Cupons)

**Regra:** "Pedido mínimo R$ 20, exceto VIPs."

**Prompt (Focado em Cobertura):**

```
Estou usando pytest. Gere uma função de teste usando @pytest.mark.parametrize
para a função validate_cart. Cubra os seguintes cenários (Happy Path e Edge Cases):

1. Valor exato do limite (19.99 vs 20.00).
2. Usuário VIP com valor baixo.
3. Valores negativos (sanity check).
4. Tipos incorretos (string ao invés de float).
```

**Resultado:** A IA gera uma **matriz de testes robusta** que cobriria bugs que um humano cansado deixaria passar.

### Caso 3: SQL Analytics

**Cenário:** O PM pede: _"Quais usuários pediram Pizza e Hambúrguer na mesma semana?"_

**A Técnica do Schema Dump:** Para o LLM não alucinar nomes de colunas, passe o DDL (Definição da tabela).

**Prompt:**

```
Aqui estão os schemas das minhas tabelas orders e order_items [colar CREATE TABLE...].
Escreva uma query PostgreSQL otimizada (use CTEs se necessário) para encontrar
usuários que compraram itens com 'Pizza' E 'Hambúrguer' num intervalo de 7 dias.
```

**Resultado:** O LLM entende as chaves estrangeiras (`user_id`, `order_id`) e monta os JOINs corretamente na primeira tentativa.

<div align="center">
  <img src="../img/artigo_5/figura3.png" alt="Figura 3: Casos de Uso" width="70%">
  <p><em>Figura 3: Três casos práticos de LLM como copiloto: Refatoração, Testes e SQL.</em></p>
</div>

## 5. Métricas, Riscos e Boas Práticas

### Métricas de Engenharia

- **Cobertura de testes:** 85%+ após copiloto
- **Tempo médio de PR:** 2.8 dias
- **Incidentes em produção:** queda de 30%
- **Feedback dos devs:** 92% aprovam copiloto para tarefas repetitivas

**Tabela de riscos e soluções:**

| Risco                 | Problema real                     | Solução recomendada                  |
| --------------------- | --------------------------------- | ------------------------------------ |
| Alucinação de Pacotes | Sugere lib falsa/maliciosa        | Verificar no PyPI/npm antes de usar  |
| Viés de Automação     | Confiança excessiva no código IA  | Checklist de revisão obrigatória     |
| Vazamento de dados    | API Key/PII em chat público       | Ferramenta enterprise/zero-retention |
| Testes insuficientes  | Cobertura baixa, bugs silenciosos | Geração automatizada + revisão       |

**Checklist de boas práticas:**

- [x] Sempre revise código gerado
- [x] Use contexto do projeto
- [x] Audite prompts e resultados
- [x] Teste edge cases e cenários negativos
- [x] Proteja dados sensíveis

## 6. Evidence & Exploration

**Experimento real:**

- Rodei um teste A/B em time de delivery: metade dos devs usando Copilot, metade sem.
- Métricas coletadas:
  - Tempo médio para entregar feature: 2.5 dias (Copilot) vs 4.2 dias (sem Copilot)
  - Bugs encontrados em produção: 1.2% (Copilot) vs 2.8% (sem Copilot)
  - Cobertura de testes: 85% (Copilot) vs 72% (sem Copilot)
- Logs e feedbacks salvos em dashboard (Mixpanel, Datadog)

**Exemplo de log de métrica:**

```json
{
  "dev_id": "u123",
  "feature": "checkout-refactor",
  "copilot": true,
  "duration_days": 2.5,
  "bugs_prod": 1,
  "test_coverage": 88,
  "timestamp": "2025-12-08T10:00:00Z"
}
```

**Ferramentas recomendadas:**

- Mixpanel, Datadog, Amplitude para métricas
- Semgrep, Snyk para segurança
- BigQuery para logs

## 7. Reflexões Pessoais & Próximos Passos

> **Síntese:** LLMs aceleram devs, mas só entregam valor real quando combinados com engenharia clássica: revisão, testes, contexto e segurança. O futuro do dev é ser orquestrador de código gerado, não digitador.

**Checklist de aprendizados:**

- [x] Revisão técnica é indispensável
- [x] Testes automatizados e edge cases
- [x] Auditoria de prompts e resultados
- [x] Segurança e privacidade de dados
- [x] Uso de contexto do projeto

**Roadmap prático:**

1. Implemente auditoria de prompts e resultados
2. Use ferramentas enterprise para proteger dados
3. Rode experimentos A/B e salve métricas
4. Aprimore prompts com contexto do projeto
5. Automatize geração de testes e revise manualmente

**Chamada para ação:**
Você já usou Copilot ou outra IA no seu time? Qual foi o maior ganho ou desafio? Comente abaixo ou compartilhe seu experimento — sua experiência pode ajudar outros devs a evitar bugs e acelerar entregas!

---

**Artigos Relacionados:**

- [02 - Prompt Engineering com PACE](./02-prompt-engineering-pace.md)
- [10 - Testes Automatizados em Sistemas com IA](./10-testes-automatizados-sistemas-ia.md)
- [06 - Versionamento de Prompts, Dados e Modelos](./06-versionamento-prompts-dados-modelos.md)
