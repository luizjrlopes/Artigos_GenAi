# A/B Testing para Features de IA: Ciência de dados aplicada à Engenharia de Prompt

![Capa: A/B Testing em IA](../img/artigo_15/capa.png)

## 1. Contexto e Propósito (Purpose)

Você mudou o prompt de recomendação de pratos para ser "mais engraçado". O time adorou. Mas será que o usuário vai comprar mais? Ou ele vai achar irritante e fechar o app?
Em produtos digitais, opinião não escala. Dados escalam.
Testar IA em produção é mais complexo que testar a cor de um botão, porque a resposta é dinâmica.

O propósito deste artigo é mostrar como estruturar experimentos controlados para validar se a **Versão B** do seu prompt (ou modelo) realmente traz mais conversão que a **Versão A**.

## 2. Abordagem (Approach)

Vamos implementar um sistema de experimentação que:

1.  **Roteia tráfego** de forma consistente (Sticky Sessions).
2.  **Captura métricas de sucesso** (Conversão, Retenção, Feedback).
3.  **Analisa os resultados** estatisticamente.

## 3. Conceitos Fundamentais

- **Feature Flag**: A chave que liga/desliga o experimento (ex: `enable_new_prompt_v2`).
- **Sticky Session**: Garantir que o usuário João sempre caia na versão B durante o teste. Se ele ver a versão A de manhã e a B de tarde, os dados ficam sujos.
- **Métrica de Guarda (Guardrail Metric)**: Uma métrica que _não pode piorar_ (ex: Latência). Se a conversão subir 10% mas a latência subir 5 segundos, o teste falhou.

## 4. Mão na Massa: Exemplo Prático

### Router de Experimento com Feature Flags

Vamos simular um teste onde comparamos o **GPT-3.5 (Controle)** com o **GPT-4 (Variante)** para gerar descrições de pratos.

```python
import hashlib
from enum import Enum

class Variant(Enum):
    CONTROL = "gpt-3.5-turbo" # Prompt curto, modelo rápido
    TREATMENT = "gpt-4-turbo" # Prompt detalhado, modelo inteligente

def get_user_variant(user_id, experiment_salt="exp_desc_v1"):
    # Hashing determinístico para garantir Sticky Session
    hash_input = f"{user_id}:{experiment_salt}"
    hash_val = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)

    # 50% para cada lado
    if hash_val % 100 < 50:
        return Variant.CONTROL
    return Variant.TREATMENT

def generate_dish_description(user_id, dish_name):
    variant = get_user_variant(user_id)

    # Loga qual variante foi usada (CRUCIAL para análise)
    logger.info("experiment_exposure", extra={
        "user_id": user_id,
        "experiment": "exp_desc_v1",
        "variant": variant.value
    })

    if variant == Variant.CONTROL:
        return call_llm(model="gpt-3.5-turbo", prompt=f"Descreva {dish_name}")
    else:
        return call_llm(model="gpt-4-turbo", prompt=f"Descreva {dish_name} de forma apetitosa e vendedora")
```

### Análise de Resultados (SQL)

Depois de rodar por uma semana, vamos ao Data Warehouse.

```sql
SELECT
    variant,
    COUNT(DISTINCT user_id) as users,
    AVG(added_to_cart) as conversion_rate,
    AVG(latency_ms) as avg_latency
FROM
    experiment_logs
WHERE
    experiment_id = 'exp_desc_v1'
GROUP BY
    1
```

**Resultado Hipotético:**

- **Control (GPT-3.5)**: 2.5% conversão, 800ms latência.
- **Treatment (GPT-4)**: 2.8% conversão, 4500ms latência.

**Decisão:** O aumento de 0.3% na conversão paga o custo extra e a latência alta? Provavelmente não para um item barato, mas talvez sim para um pedido grande.

## 5. Métricas, Riscos e Boas Práticas

### Riscos

- **Efeito Novidade**: O usuário interage mais só porque mudou, não porque é melhor. Espere o efeito passar (pelo menos 1 ou 2 semanas).
- **Interferência**: Rodar dois testes na mesma página (ex: mudar a foto E a descrição ao mesmo tempo) torna impossível saber o que causou a melhoria.

### Boas Práticas

- **Comece Pequeno**: Lance para 1% dos usuários, depois 5%, depois 50%. Se o GPT-4 quebrar, você só afetou 1%.
- **Logue o Prompt Exato**: No log de exposição, guarde a versão do prompt (`v1` ou `v2`).

## 6. Evidence & Exploration

Ferramentas como **Statsig**, **LaunchDarkly** ou **PostHog** já têm suporte nativo para testes A/B e facilitam muito a análise estatística (p-value, intervalo de confiança).
Não confie apenas na média. Olhe a distribuição. Talvez a Variante B seja ótima para usuários Power Users mas terrível para novos usuários.

## 7. Reflexões Pessoais & Próximos Passos

A intuição é o início da hipótese, mas os dados são o juiz final. Em GenAI, onde tudo parece "mágico", ser cético e orientado a dados é o que diferencia engenharia de empolgação.
Mas e quando o modelo começa a inventar coisas que não existem?

No próximo artigo, vamos falar sobre **Alucinações de LLM e Mitigação**: como impedir que seu bot prometa pizza grátis ou invente ingredientes perigosos.
