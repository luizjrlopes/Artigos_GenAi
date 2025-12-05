#!/usr/bin/env python3

"""
Valida a estrutura dos artigos em articles/:

1. Verifica se seguem as seções esperadas
2. Valida se existe capa (capa.png) como primeiro elemento
3. Rastreia quais figuras (figura1-4) existem vs. são referenciadas
4. Indica como gerar as imagens faltantes manualmente
"""

import re
from pathlib import Path

REQUIRED_SECTIONS = [
    "## 1. Contexto e Propósito",
    "## 2. Abordagem",
    "## 3. Conceitos Fundamentais",
    "## 4. Mão na Massa: Exemplo Prático",
    "## 5. Métricas, Riscos e Boas Práticas",
    "## 6. Evidence & Exploration",
    "## 7. Reflexões Pessoais & Próximos Passos",
]

EXPECTED_FIGURES = ["capa.png", "figura1.png", "figura2.png", "figura3.png", "figura4.png"]

def extract_article_number(filename):
    """Extrai o número do artigo do nome do arquivo"""
    match = re.match(r'(\d+)-', filename)
    return int(match.group(1)) if match else None

def extract_images_from_markdown(text):
    """Extrai todas as referências de imagens do markdown"""
    pattern = r'!\[(.*?)\]\(\.\.\/img\/artigo_(\d+)\/(.*?)\)'
    matches = re.findall(pattern, text)
    # Retorna lista de (título, artigo_num, filename)
    return matches

def extract_context_for_figure(text, figure_name):
    """Extrai contexto sobre a figura (parágrafo anterior/seguinte no markdown)"""
    # Procura pela referência da figura
    pattern = rf'!\[.*?\]\(.*?{figure_name}\).*?[\n_]?(.*?)[\n]'
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return "Contexto não encontrado"

def main():
    base_dir = Path(__file__).resolve().parents[1]
    articles_dir = base_dir / "articles"
    img_dir = base_dir / "img"

    print("=" * 80)
    print("VALIDAÇÃO COMPLETA DE ARTIGOS E IMAGENS")
    print("=" * 80)
    print()

    articles = sorted(articles_dir.glob("*.md"))
    
    for md in articles:
        text = md.read_text(encoding="utf-8")
        article_num = extract_article_number(md.name)
        img_article_dir = img_dir / f"artigo_{article_num}"
        
        print(f"\n📄 {md.name}")
        print("-" * 80)
        
        # 1. Validar seções
        missing_sections = [s for s in REQUIRED_SECTIONS if s not in text]
        if missing_sections:
            print(f"  ⚠️  SEÇÕES FALTANDO:")
            for s in missing_sections:
                print(f"     - {s}")
        else:
            print(f"  ✅ Todas as seções obrigatórias presentes")
        
        # 2. Validar imagens referenciadas
        referenced_images = extract_images_from_markdown(text)
        
        if not referenced_images:
            print(f"  ❌ NENHUMA IMAGEM REFERENCIADA NO ARTIGO!")
        else:
            # Checar se capa é a primeira referência
            first_ref = referenced_images[0]
            if first_ref[2] != "capa.png":
                print(f"  ⚠️  CAPA NÃO É O PRIMEIRO ELEMENTO (encontrado: {first_ref[2]})")
            else:
                print(f"  ✅ Capa é o primeiro elemento do artigo")
            
            print(f"\n  📊 IMAGENS REFERENCIADAS:")
            
            # Criar pasta se não existir para referência
            img_article_dir.mkdir(parents=True, exist_ok=True)
            
            for title, art_num, filename in referenced_images:
                img_path = img_article_dir / filename
                exists = "✅" if img_path.exists() else "❌"
                print(f"     {exists} {filename:20} | {title}")
                
                if not img_path.exists():
                    # Extrair contexto para gerar manualmente
                    context = extract_context_for_figure(text, filename)
                    print(f"        └─ Descrição: {context}")
        
        print()

if __name__ == "__main__":
    main()
