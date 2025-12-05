#!/usr/bin/env python3

"""
Gera READMEs em cada img/artigo_X/ com especificações DETALHADAS de como
as figuras 1-4 devem ser geradas baseado no conteúdo dos artigos.

Extrai:
- Título e descrição exata da figura
- Contexto completo antes e depois da referência
- Seções relevantes que explicam o que a figura deve mostrar
"""

import re
from pathlib import Path

def extract_article_number(filename):
    """Extrai o número do artigo do nome do arquivo"""
    match = re.match(r'(\d+)-', filename)
    return int(match.group(1)) if match else None

def extract_figure_specs(text, figure_num):
    """
    Extrai especificações COMPLETAS de uma figura:
    - Título/descrição exata
    - Contexto antes (parágrafo anterior)
    - Seção depois (conteúdo relacionado)
    - Qualquer tabela ou lista que acompanha
    """
    specs = {
        'title': None,
        'description': None,
        'context_before': None,
        'context_after': None,
        'has_table': False,
        'table_content': None
    }
    
    # 1. Extrair título e descrição: ![Figura N: Título](../img/artigo_X/figuraY.png)
    title_pattern = rf'!\[(.*?Figura {figure_num}:.*?)\]\(.*?figura{figure_num}\.png\)'
    title_match = re.search(title_pattern, text)
    if title_match:
        specs['title'] = title_match.group(1).strip()
    
    # 2. Extrair descrição em itálico: _Figura N: descrição_
    desc_pattern = rf'!\[.*?Figura {figure_num}:.*?\]\(.*?figura{figure_num}\.png\)\s*\n_([^_]*?)_'
    desc_match = re.search(desc_pattern, text)
    if desc_match:
        specs['description'] = desc_match.group(1).strip()
    
    # 3. Extrair contexto ANTES da figura (parágrafo anterior)
    before_pattern = rf'((?:[^!]|\n(?!!))*?)\n![^]]*?Figura {figure_num}:'
    before_match = re.search(before_pattern, text, re.DOTALL)
    if before_match:
        content = before_match.group(1).strip()
        # Pega últimos 1-2 parágrafos antes
        paras = [p.strip() for p in content.split('\n\n') if p.strip() and not p.startswith('#')]
        if paras:
            specs['context_before'] = '\n\n'.join(paras[-2:])
    
    # 4. Extrair contexto DEPOIS da figura (próxima seção/parágrafo)
    after_pattern = rf'!\[.*?Figura {figure_num}:.*?\]\(.*?figura{figure_num}\.png\)\s*\n(?:_.*?_\s*\n)?(.*?)(?=(?:\n##\s|\n\|.*\|.*\||!\[.*Figura \d+:))'
    after_match = re.search(after_pattern, text, re.DOTALL)
    if after_match:
        content = after_match.group(1).strip()
        # Limita a 3 parágrafos
        paras = [p.strip() for p in content.split('\n\n') if p.strip()][:3]
        if paras:
            specs['context_after'] = '\n\n'.join(paras)
    
    # 5. Verificar se há tabela próxima
    table_pattern = rf'(?:!\[.*?Figura {figure_num}:.*?\]\(.*?\).*?\n)?(\|.*?\|.*?(?:\n\|.*?\|.*?)*)'
    table_match = re.search(table_pattern, text, re.DOTALL)
    if table_match:
        specs['has_table'] = True
        specs['table_content'] = table_match.group(1).strip()
    
    return specs


def generate_readme_for_article(article_num, article_path, img_dir_path):
    """
    Gera README para um artigo específico com specs DETALHADAS de figuras 1-4
    """
    text = article_path.read_text(encoding="utf-8")
    title_match = re.match(r'# (.*?)\n', text)
    title = title_match.group(1) if title_match else f"Artigo {article_num}"
    
    readme_content = f"""# Especificações de Imagens - Artigo {article_num}

## {title}

**Instruções:** As imagens abaixo devem ser geradas profissionalmente. Este README detalha exatamente o que cada figura deve conter com base no conteúdo do artigo.

---

## Capa (capa.png)

**Status:** ✅ Gerada

A imagem de capa deve representar visualmente o tema principal: **{title}**

---

"""
    
    # Figuras 1-4
    for fig_num in range(1, 5):
        specs = extract_figure_specs(text, fig_num)
        
        readme_content += f"## Figura {fig_num} (figura{fig_num}.png)\n\n"
        
        # Título/Label da figura
        if specs['title']:
            readme_content += f"**Título:** {specs['title']}\n\n"
        
        # Descrição exata
        if specs['description']:
            readme_content += f"**Descrição:** {specs['description']}\n\n"
        
        # Contexto ANTES (por que esta figura?)
        if specs['context_before']:
            readme_content += f"### O que precisa ser mostrado (contexto antes):\n\n{specs['context_before']}\n\n"
        
        # Contexto DEPOIS (como usar esta figura?)
        if specs['context_after']:
            readme_content += f"### Como a figura é utilizada (contexto depois):\n\n{specs['context_after']}\n\n"
        
        # Tabela relacionada
        if specs['has_table']:
            readme_content += f"### Dados/Tabela relacionada:\n\n```\n{specs['table_content']}\n```\n\n"
        
        # Se nenhum contexto foi extraído, aviso
        if not specs['context_before'] and not specs['context_after'] and not specs['description']:
            readme_content += "⚠️ **Nota:** Consulte o artigo original para entender o contexto desta figura.\n\n"
        
        readme_content += "---\n\n"
    
    # Guia geral
    readme_content += """## 📋 Guia Geral de Criação

### Ferramentas Recomendadas
- Figma, Adobe XD, Canva Pro
- Python (Matplotlib, Pillow) para diagramas técnicos
- Qualquer plataforma de design que exporte PNG de alta qualidade

### Especificações Técnicas
- **Formato:** PNG (sem fundo ou fundo branco/claro)
- **Dimensões:** Mínimo 1200x800px
- **Resolução:** 300 DPI (para impressão profissional)
- **Qualidade:** Vetorial ou Alta resolução (não pixelada)

### Paleta de Cores Recomendada
```
Azul Profissional:    #2C5282
Verde:                #38A169
Vermelho:             #E53E3E
Cinza Escuro:         #718096
Cinza Claro:          #E2E8F0
Branco:               #FFFFFF
Amarelo Destaque:     #ECC94B
Fundo Claro:          #F7FAFC
```

### Tipografia
- **Fonte:** Sans-serif (Arial, Helvetica, Roboto, Inter)
- **Tamanho:** Legível em tamanho pequeno
- **Cor do Texto:** Cinza escuro (#2D3748) ou azul (#2C5282)

### Estilo
- Mantém consistência com o design dos artigos anteriores
- Limpo e minimalista
- Com legendas e anotações claras
- Usar ícones ou símbolos para facilitar compreensão

---

## ✅ Checklist de Conclusão

Marque conforme as figuras forem criadas:

- [x] Capa (capa.png)
- [ ] Figura 1 (figura1.png)
- [ ] Figura 2 (figura2.png)
- [ ] Figura 3 (figura3.png)
- [ ] Figura 4 (figura4.png)

**Última Atualização:** 2025-12-05
**Artigo:** {article_num} - {title}
"""
    
    return readme_content

def main():
    base_dir = Path(__file__).resolve().parents[1]
    articles_dir = base_dir / "articles"
    img_dir = base_dir / "img"
    
    print("=" * 80)
    print("GERANDO READMEs COM ESPECIFICAÇÕES DETALHADAS DE IMAGENS")
    print("=" * 80)
    print()
    
    articles = sorted(articles_dir.glob("*.md"))
    
    for md_file in articles:
        article_num = extract_article_number(md_file.name)
        if not article_num:
            continue
        
        img_article_dir = img_dir / f"artigo_{article_num}"
        img_article_dir.mkdir(parents=True, exist_ok=True)
        
        readme_path = img_article_dir / "README.md"
        
        # Gerar README
        readme_content = generate_readme_for_article(article_num, md_file, img_article_dir)
        readme_path.write_text(readme_content, encoding="utf-8")
        
        print(f"✅ README gerado: img/artigo_{article_num}/README.md")
    
    print()
    print("=" * 80)
    print("CONCLUÍDO! Todos os READMEs foram gerados com especificações detalhadas.")
    print("=" * 80)

if __name__ == "__main__":
    main()
