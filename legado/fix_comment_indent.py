# -*- coding: utf-8 -*-
from pathlib import Path
BASE = Path(r"c:\Users\luizj\OneDrive\Área de Trabalho\artigos\genai-delivery-engineering-notes\Artigos_GenAi")
files = [
    "html/09-arquiteturas-event-driven-ia.html",
    "html/10-testes-automatizados-sistemas-ia.html",
    "html/11-basico-mlops-llmops.html",
    "html/12-monitorando-qualidade-respostas.html",
    "html/13-logging-metricas-genai.html",
    "html/14-custos-ia-chamadas-modelo.html",
    "html/15-ab-testing-features-ia.html",
    "html/16-alucinacoes-llm-mitigacao.html",
    "html/17-bias-modelos-ia.html",
    "html/18-interfaces-conversacionais-honestas.html",
    "html/19-colaboracao-humano-ia.html",
    "html/20-jornada-genai-produtos-digitais.html",
]
for rel in files:
    path = BASE / rel
    text = path.read_text(encoding='utf-8')
    text = text.replace("</section>\r\n\r\n<!-- 1.", "</section>\r\n\r\n        <!-- 1.")
    text = text.replace("</section>\n\n<!-- 1.", "</section>\n\n        <!-- 1.")
    path.write_text(text, encoding='utf-8')
