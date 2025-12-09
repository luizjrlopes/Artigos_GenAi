# Tratamento de Erros e Timeouts: Quando o LLM te deixa na mão (e como sobreviver)

<div align="center">
  <img src="../img/artigo_8/capa.png" alt="Capa: Tratamento de erros em LLM" width="70%">
</div>

## 1. Contexto e Propósito (Purpose)

Em um app de delivery, se o serviço de pagamento cai, você não deixa o usuário tentar pagar infinitamente; você avisa que deu erro. Com LLMs, a instabilidade é a regra, não a exceção.
APIs de IA sofrem de _Rate Limits_ agressivos, latência variável e sobrecarga frequente. Se o seu código não estiver preparado para falhar, seu produto vai parecer amador.

O propósito deste artigo é ensinar como construir uma camada de **resiliência** em volta das chamadas de LLM, garantindo que o usuário final tenha uma experiência decente mesmo quando a OpenAI (ou qualquer outro provider) estiver pegando fogo.

## 2. Abordagem (Approach)

Vamos categorizar os erros mais comuns e implementar padrões de defesa:

1.  **Erros Transientes (429, 500, Timeouts)**: Resolvidos com Retries inteligentes.
2.  **Erros Lógicos (Context Window, Bad Request)**: Resolvidos com Truncamento e Validação.
3.  **Falha Total**: Resolvida com Fallbacks e Degradação Graciosa.

## 3. Conceitos Fundamentais

- **Exponential Backoff**: Não tente de novo imediatamente. Espere 1s, depois 2s, depois 4s. Isso evita derrubar ainda mais um serviço que já está instável.
- **Jitter**: Adicionar um tempo aleatório ao backoff para evitar que todos os seus servidores tentem reconectar no exato mesmo milissegundo.
- **Circuit Breaker**: Se o serviço falhou 10 vezes seguidas, pare de tentar por um tempo e retorne erro imediatamente.

## 4. Mão na Massa: Exemplo Prático

### Implementando um Decorator de Resiliência em Python

Vamos usar a biblioteca `tenacity` para criar uma chamada robusta.

```python
import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type
)

# Configuração: Tentar até 3 vezes, esperando entre 1s e 10s (exponencial + jitter)
@retry(
    retry=retry_if_exception_type((openai.APIConnectionError, openai.RateLimitError, openai.APITimeoutError)),
    wait=wait_random_exponential(multiplier=1, max=10),
    stop=stop_after_attempt(3)
)
def call_llm_robust(prompt):
    print("Tentando chamar API...")
    return openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        timeout=15 # Timeout curto no client-side para não travar a thread
    )

def get_restaurant_summary(restaurant_id):
    try:
        response = call_llm_robust(f"Resuma as reviews do restaurante {restaurant_id}")
        return response.choices[0].message.content
    except Exception as e:
        # FALLBACK: Se tudo der errado, não quebre a tela do usuário.
        print(f"Erro fatal após retries: {e}")
        return "Desculpe, não conseguimos gerar o resumo agora. Mas o restaurante tem nota 4.8!"
```

### Lidando com Context Window Exceeded

Se o erro for "prompt too long", retry não adianta. Você precisa cortar o texto.

```python
import tiktoken

def truncate_text(text, max_tokens=3000):
    encoder = tiktoken.encoding_for_model("gpt-4")
    tokens = encoder.encode(text)
    if len(tokens) > max_tokens:
        # Corta o excesso e decodifica de volta
        return encoder.decode(tokens[:max_tokens])
    return text
```

## 5. Métricas, Riscos e Boas Práticas

### Riscos

- **Custo de Retry**: Se você paga por token de entrada, e a API falha no final da geração, o retry vai te cobrar a entrada de novo.
- **Cascading Failure**: Se seu retry for muito agressivo, você pode derrubar seus próprios sistemas internos que dependem dessa resposta.

### Boas Práticas

- **Timeouts Client-Side**: Nunca confie no timeout padrão da biblioteca. Defina explicitamente (ex: 30s).
- **Fallback Estático**: Tenha sempre uma resposta "burra" pronta. É melhor mostrar "Descrição indisponível" do que "Error 500: Internal Server Error".

## 6. Evidence & Exploration

### Teste Prático 1: Simulação de Falhas

Implemente em um ambiente de staging:

**Bloqueie a URL da OpenAI no Firewall:**

```bash
# No seu firewall/proxy, rejeite conexões para api.openai.com
# ou simule timeout alterando o hosts file
```

**Verifique o comportamento:**

- ❌ App trava ou mostra "Error 500"?
- ✅ App mostra fallback gracioso em segundos?

**Métrica esperada:**

```
Sem retry: 1 tentativa, ~30s de timeout, erro ao usuário
Com retry + backoff: 3 tentativas, ~15s total, fallback em 20s
```

### Teste Prático 2: Rate Limit Simulado

Você tem limite de 100 requests/minuto na OpenAI. Com 50 usuários simultâneos, você ultrapassa. O que acontece?

```python
from unittest.mock import patch
import openai

def test_rate_limit_handling():
    # Simula erro 429 nas 2 primeiras tentativas
    with patch('openai.chat.completions.create') as mock:
        mock.side_effect = [
            openai.RateLimitError("Rate limit exceeded"),
            openai.RateLimitError("Rate limit exceeded"),
            {"choices": [{"message": {"content": "Sucesso na 3ª tentativa"}}]}
        ]

        response = call_llm_robust("Teste")
        assert mock.call_count == 3  # 3 tentativas
        assert "Sucesso" in response
```

**Logs esperados:**

```
[10:30:00] Tentativa 1 - RateLimitError
[10:30:01] Esperando 1.2s...
[10:30:01] Tentativa 2 - RateLimitError
[10:30:03] Esperando 3.8s...
[10:30:07] Tentativa 3 - Success
```

O espaçamento exponencial é evidente.

### Teste Prático 3: Context Window Overflow

Você pede um resumo de 10,000 reviews. O LLM reclama:

```json
{
  "error": {
    "message": "This model's maximum context length is 8192 tokens",
    "type": "invalid_request_error"
  }
}
```

Com truncamento automático:

```python
@retry(...)
def safe_summarize(reviews_text):
    # Trunca para 6000 tokens antes de enviar (deixa margem)
    safe_text = truncate_text(reviews_text, max_tokens=6000)
    return call_llm_robust(f"Resuma: {safe_text}")

# Teste: enviando 20,000 tokens de reviews
big_text = "review 1... " * 2000
summary = safe_summarize(big_text)  # Vai truncar para 6000 e não vai dar erro
```

### Ferramentas de Observabilidade

- **Sentry**: Capture exceções e veja padrões de erro
- **Datadog APM**: Rastreie latência de retries
- **OpenTelemetry**: Instrumente cada tentativa com spans (visibilidade completa)
- **Custom Logging**: Log estruturado com `attempt_number`, `wait_time`, `error_type`

## 7. Reflexões Pessoais & Próximos Passos

### A Lição: Código Defensivo é Código Honesto

Resiliência é o que separa demos de produtos reais. Em demos, se der erro, você dá F5 e ninguém vê. Em produção, se der erro, o usuário:

1. Vê uma tela branca
2. Tenta de novo (desperdiça dados)
3. Vai para o concorrente

Implementar retry + backoff exponencial + fallbacks não é "over-engineering"—é **respeito pelo usuário**.

A linha entre "código que funciona" e "código que o usuário confia" é feita de tratamento de erros.

### Conectando com a Série

Agora temos:

- ✅ Prompts versionados (Artigo 06)
- ✅ APIs bem desenhadas (Artigo 07)
- ✅ Tratamento de erro robusto (Artigo 08)

Mas se você está fazendo tudo em **request/response síncrono**, não vai escalar. Quando um usuário gera um relatório de 1GB de dados, ele não pode esperar 5 minutos com a conexão aberta.

### Próximos Passos

1. **Implemente retry + backoff hoje**: Copie o código do decorator acima.
2. **Teste falhas**: Bloqueie a API, force rate limits, veja o comportamento.
3. **Meça**: MTTR (Mean Time To Recovery), latência P99, taxa de erro.
4. **Leia o Artigo 09**: Vamos falar sobre **Arquiteturas Event-Driven para IA**: como desacoplar completamente a geração de texto do fluxo de requisição do usuário. Porque nem tudo precisa ser síncrono.
