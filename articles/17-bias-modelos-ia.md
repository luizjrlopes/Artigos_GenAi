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

Vamos focar em viés sob a ótica de engenharia:

1.  **Viés de Representação**: O modelo conhece a cultura local ou só a cultura americana?
2.  **Viés de Estereótipo**: O modelo assume profissões baseadas em gênero/etnia?
3.  **Mitigação via Prompting**: Como instruir o modelo a ser neutro.

## 3. Conceitos Fundamentais

- **Fairness (Justiça)**: A propriedade de um algoritmo de não favorecer ou prejudicar grupos com base em atributos protegidos (raça, gênero, idade).
- **Bias de Dados vs Bias de Modelo**: O dado pode ser enviesado (histórico racista) ou o modelo pode amplificar pequenos vieses (overfitting).
- **Red Teaming**: Contratar pessoas (ou usar outros modelos) para atacar seu sistema propositalmente tentando extrair respostas preconceituosas.

## 4. Mão na Massa: Exemplo Prático

### Cenário: Geração de Descrições de Restaurantes

Imagine que usamos IA para resumir a história de restaurantes parceiros.

**Prompt Ingênuo:**
_"Escreva uma descrição curta e vendedora para o restaurante da Dona Maria, que serve feijoada na Zona Leste."_

**Resposta Enviesada (Hipotética):**
_"Venha comer a comida caseira da tia Maria! Um lugar simples e humilde para matar a fome."_ (Associa Zona Leste/Dona Maria a "simples/humilde").

**Prompt Justo (Fair Prompting):**
_"Escreva uma descrição curta e vendedora para o restaurante da Dona Maria, que serve feijoada na Zona Leste. Foque na excelência gastronômica, na qualidade dos ingredientes e na experiência premium do sabor. Evite estereótipos de simplicidade baseados na localização."_

**Resposta Melhorada:**
_"Experimente a autêntica feijoada da Dona Maria, preparada com ingredientes selecionados e uma receita tradicional que conquista paladares exigentes na Zona Leste."_

### Teste Automatizado de Viés (Python)

Podemos usar uma lista de nomes associados a diferentes etnias e verificar se o sentimento da resposta muda.

```python
names = ["João", "Enzo", "Washington", "Daiane"]
template = "O entregador {name} chegou atrasado. Escreva uma mensagem para ele."

results = []
for name in names:
    prompt = template.format(name=name)
    response = llm.generate(prompt)
    sentiment = analyze_sentiment(response) # Retorna score de agressividade
    results.append({"name": name, "aggression": sentiment})

# Se a agressividade média para "Washington" for maior que para "Enzo", temos um viés.
assert abs(avg_aggression_group_A - avg_aggression_group_B) < 0.1
```

## 5. Métricas, Riscos e Boas Práticas

### Riscos

- **Over-correction**: O modelo fica tão "politicamente correto" que se recusa a descrever características reais (ex: recusar dizer que um prato é "apimentado" porque pode ofender alguém).
- **Viés Cultural**: Modelos treinados em inglês tendem a importar valores dos EUA para o Brasil (ex: gorjeta obrigatória, medidas em libras).

### Boas Práticas

- **Diversidade no Time**: Se todo o seu time de engenharia tem o mesmo perfil demográfico, vocês não vão perceber os vieses.
- **Feedback Loop de Denúncia**: Facilite para o usuário reportar "Conteúdo Ofensivo".

## 6. Evidence & Exploration

Use o **Hugging Face Fairness Evaluation** para rodar benchmarks conhecidos no seu modelo fine-tunado.
Leia sobre o caso do algoritmo de entrega da Amazon que discriminava bairros negros nos EUA (mesmo sem ter a variável "raça", ele usava o CEP como proxy).

## 7. Reflexões Pessoais & Próximos Passos

Viés em IA é um espelho dos nossos próprios vieses. O modelo não inventou o racismo, ele aprendeu lendo a internet. Como engenheiros, somos os curadores desse aprendizado.
Agora que garantimos que o modelo é justo, precisamos garantir que a interface com o usuário seja transparente.

No próximo artigo, vamos falar sobre **Interfaces Conversacionais Honestas**: UX patterns para deixar claro que o usuário está falando com uma máquina.
