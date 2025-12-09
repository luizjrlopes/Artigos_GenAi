#!/usr/bin/env python3
"""
Validador de artigos Markdown baseado no Guia de Profundidade e Estrutura de LinkedIn.

O script verifica:

1. Estrutura (seções obrigatórias)
2. Profundidade (palavras, checklist, estrutura visual)
3. Qualidade para LinkedIn (gancho, CTA, legibilidade)
4. Imagens de capa (referência e existência básica)

Uso:

    python validate-article-guide.py path/para/pasta_com_artigos

Cada artigo deve ser um .md com título em nível 1 (#) e seções em nível 2 (##).
"""

import sys
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional


# ---------------------------------------------------------------------
# Configurações de seções e profundidade
# ---------------------------------------------------------------------

@dataclass
class SectionConfig:
    prefix: str           # prefixo do título, usado com startswith
    description: str
    min_words: int
    checklist: List[str] = field(default_factory=list)


REQUIRED_SECTIONS: List[SectionConfig] = [
    SectionConfig(
        prefix="## 1. Contexto e Propósito",
        description="Relevância de mercado, impacto prático e por que isso importa.",
        min_words=150,
        checklist=["relevância", "mercado", "empresa", "impacto", "problema"]
    ),
    SectionConfig(
        prefix="## 2. Abordagem",
        description="Visão geral da solução, fluxo macro, caso prático.",
        min_words=100,
        checklist=["fluxo", "solução", "arquitetura", "caso", "exemplo"]
    ),
    SectionConfig(
        prefix="## 3. Conceitos Fundamentais",
        description="Definições claras, exemplos aplicados, mudança de mindset.",
        min_words=150,
        checklist=["conceito", "definição", "exemplo", "mindset"]
    ),
    SectionConfig(
        prefix="## 4. Mão na Massa",
        description="Implementação prática, código, passo a passo.",
        min_words=300,
        checklist=["código", "implementação", "passo", "fluxo", "endpoint"]
    ),
    SectionConfig(
        prefix="## 5. Métricas, Riscos e Boas Práticas",
        description="Latência, custo, confiabilidade, boas práticas de engenharia.",
        min_words=200,
        checklist=["métrica", "latência", "custo", "risco", "prática", "alerta"]
    ),
    SectionConfig(
        prefix="## 6. Evidence & Exploration",
        description="Testes, logs, feedback, validação de impacto.",
        min_words=150,
        checklist=["teste", "log", "feedback", "resultado", "experimento"]
    ),
    SectionConfig(
        prefix="## 7. Reflexões Pessoais & Próximos Passos",
        description="Síntese, lições aprendidas, próximos artigos ou melhorias.",
        min_words=120,
        checklist=["aprendi", "lição", "reflexão", "próximos", "futuro"]
    ),
]


# ---------------------------------------------------------------------
# Utilitários de parsing
# ---------------------------------------------------------------------


def extract_title(text: str) -> Optional[str]:
    """Extrai o título principal (# Título)"""
    match = re.search(r'^# (.+)$', text, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def split_sections(text: str) -> Dict[str, str]:
    """
    Divide o artigo em seções baseadas em headings de nível 2 (##).

    Retorna dict: {titulo_da_secao: conteudo}
    """
    sections: Dict[str, str] = {}
    pattern = re.compile(r'^(## .+)$', flags=re.MULTILINE)
    matches = list(pattern.finditer(text))

    if not matches:
        return sections

    for idx, m in enumerate(matches):
        title = m.group(1).strip()
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        sections[title] = body

    return sections


def match_required_sections(sections: Dict[str, str]) -> Tuple[Dict[str, Tuple[str, str]], List[SectionConfig]]:
    """
    Faz matching de cada SectionConfig com uma seção real do artigo,
    usando startswith no prefixo configurado.

    Retorna:
        - dict: {prefixo_config: (titulo_real, conteudo)}
        - lista de configs que não foram encontrados (faltando)
    """
    mapping: Dict[str, Tuple[str, str]] = {}
    missing: List[SectionConfig] = []

    for config in REQUIRED_SECTIONS:
        found_key = None
        for real_title in sections.keys():
            if real_title.startswith(config.prefix):
                found_key = real_title
                break
        if found_key:
            mapping[config.prefix] = (found_key, sections[found_key])
        else:
            missing.append(config)

    return mapping, missing


def count_words(text: str) -> int:
    """Conta palavras simples no texto."""
    tokens = re.findall(r'\w+', text, flags=re.UNICODE)
    return len(tokens)


def has_list_or_bold(text: str) -> bool:
    """Checa se há listas ou negrito no conteúdo da seção."""
    if re.search(r'(^\s*[-*]\s+)', text, flags=re.MULTILINE):
        return True
    if "**" in text:
        return True
    return False


# ---------------------------------------------------------------------
# Avaliação de profundidade por seção
# ---------------------------------------------------------------------


def assess_section_depth(config: SectionConfig, content: str) -> float:
    """
    Retorna um score 0–100 para a seção:

    - Até 60 pts por atingir o mínimo de palavras
    - Até 25 pts por cobrir itens da checklist
    - 0–15 pts por estrutura visual (listas, negrito)
    """
    words = count_words(content)
    if words == 0:
        return 0.0

    # componente 1: tamanho
    size_ratio = min(1.0, words / config.min_words)
    size_score = 60.0 * size_ratio

    # componente 2: checklist de termos
    hits = 0
    lowered = content.lower()
    for term in config.checklist:
        if term.lower() in lowered:
            hits += 1
    checklist_ratio = hits / len(config.checklist) if config.checklist else 1.0
    checklist_score = 25.0 * checklist_ratio

    # componente 3: estrutura visual
    structure_score = 15.0 if has_list_or_bold(content) else 0.0

    return min(100.0, size_score + checklist_score + structure_score)


# ---------------------------------------------------------------------
# Avaliações específicas de LinkedIn (gancho, CTA, legibilidade)
# ---------------------------------------------------------------------


def extract_intro(text: str) -> str:
    """Pega o trecho entre o título # e a primeira seção ## (ou até o fim)."""
    # Remove título
    text_wo_title = re.sub(r'^# .+$', '', text, flags=re.MULTILINE).strip()
    # Corta na primeira seção
    m = re.search(r'^## ', text_wo_title, flags=re.MULTILINE)
    if m:
        return text_wo_title[:m.start()].strip()
    return text_wo_title.strip()


def extract_cta_block(text: str, lines: int = 6) -> str:
    """Últimas N linhas não vazias do artigo (para achar CTA)."""
    raw_lines = [l for l in text.strip().splitlines() if l.strip()]
    if not raw_lines:
        return ""
    return "\n".join(raw_lines[-lines:])


def has_hook(intro_text: str) -> bool:
    """Heurística para detectar gancho na introdução."""
    patterns = [
        r'\?',                           # pergunta
        r'\d+%',                         # estatística
        r'\b(ontem|certa vez|uma vez)\b',
        r'\b(erro|bug|quebrou|falhou)\b',
        r'\b(descobri|aprendi|percebi)\b',
    ]
    intro = intro_text.lower()
    return any(re.search(p, intro) for p in patterns)


def has_cta(ending_block: str) -> bool:
    """Heurística para detectar CTA no final (pergunta/convite)."""
    block = ending_block.lower()
    patterns = [
        r'\?',  # qualquer pergunta
        r'\b(comenta|comente|me conta|me conte|compartilha|compartilhe)\b',
        r'\b(o que você acha|já passou por isso)\b',
    ]
    return any(re.search(p, block) for p in patterns)


def assess_readability(text: str) -> float:
    """
    Score 0–100 de legibilidade simples:

    - Punição para linhas gigantes (> 200 caracteres)
    - Punição para blocos sem quebras
    """
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        return 0.0

    long_lines = sum(1 for l in lines if len(l) > 200)
    ratio_long = long_lines / len(lines)

    # Score inversamente proporcional ao número de linhas gigantes
    score = 100.0 * (1.0 - min(1.0, ratio_long))
    # Clamp
    return max(0.0, min(100.0, score))


def assess_linkedin_quality(text: str) -> float:
    """
    Score agregado para qualidade "estilo LinkedIn":

    - 30 pts gancho
    - 30 pts CTA
    - 40 pts legibilidade
    """
    intro = extract_intro(text)
    end_block = extract_cta_block(text)

    hook_score = 30.0 if has_hook(intro) else 0.0
    cta_score = 30.0 if has_cta(end_block) else 0.0
    readability_score = 40.0 * (assess_readability(text) / 100.0)

    return hook_score + cta_score + readability_score


# ---------------------------------------------------------------------
# Imagens / capa
# ---------------------------------------------------------------------


def extract_images(text: str) -> List[str]:
    """
    Extrai caminhos de imagens do markdown: ![alt](path)
    """
    results: List[str] = []

    # 1) Markdown imagem: ![alt](path)
    md_pattern = re.compile(r'!\[[^\]]*\]\(([^)]+)\)')
    results.extend(md_pattern.findall(text))

    # 2) HTML <img src="path" ...>
    html_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', flags=re.IGNORECASE)
    results.extend(html_pattern.findall(text))

    # Normalize and deduplicate while preserving order
    seen = set()
    dedup: List[str] = []
    for r in results:
        r = r.strip()
        if r and r not in seen:
            seen.add(r)
            dedup.append(r)

    return dedup


def assess_images(text: str, article_path: Path) -> Tuple[float, List[str]]:
    """
    - Verifica se há pelo menos uma imagem
    - Tenta identificar capa (nome contendo 'capa')
    - Verifica se o arquivo existe (quando caminho é relativo)
    """
    warnings: List[str] = []
    images = extract_images(text)
    if not images:
        warnings.append("Nenhuma imagem encontrada no artigo. Recomenda-se adicionar ao menos a imagem de capa (ex: 'capa.jpg').")
        # Sem nenhuma imagem, penalizamos mais — capa é obrigatória segundo novo requisito
        return 40.0, warnings

    # Procurar especificamente por imagem de capa (nome contendo 'capa')
    has_cover = any("capa" in Path(img).name.lower() for img in images)

    # Se houver capa, damos nota alta; demais imagens são opcionais
    if has_cover:
        score = 90.0
        # bônus se ao menos uma imagem referenciada existir localmente
        for img in images:
            p = (article_path.parent / img).resolve()
            if p.exists():
                score = 100.0
                break
        return min(100.0, score), warnings

    # Não há capa — se existem outras imagens, nota intermediária e aviso
    warnings.append("Não foi encontrada imagem de capa (nome contendo 'capa'). Apenas a capa é obrigatória para este validador.")
    # Se existem imagens mas sem capa, damos uma nota média
    score = 60.0
    # pequeno bônus se pelo menos uma imagem local existe
    for img in images:
        p = (article_path.parent / img).resolve()
        if p.exists():
            score += 10.0
            break

    return min(100.0, score), warnings


# ---------------------------------------------------------------------
# Formatação geral
# ---------------------------------------------------------------------


def assess_formatting(text: str) -> float:
    """
    Score de formatação:

    - Punição para parágrafos extremamente longos (> 400 caracteres)
    - Bônus se há uso de negrito/listas no texto como um todo
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        return 0.0

    long_par = sum(1 for p in paragraphs if len(p) > 400)
    ratio_long = long_par / len(paragraphs)

    base = 100.0 * (1.0 - min(1.0, ratio_long))

    # bônus se usar algum destaque
    if "**" in text or re.search(r'(^\s*[-*]\s+)', text, flags=re.MULTILINE):
        base += 5.0

    return max(0.0, min(100.0, base))


# ---------------------------------------------------------------------
# Função principal de avaliação de um artigo
# ---------------------------------------------------------------------


@dataclass
class ArticleReport:
    path: Path
    title: str
    number: Optional[int]
    depth_score: float
    linkedin_score: float
    formatting_score: float
    image_score: float
    final_score: float
    missing_sections: List[str]
    section_scores: Dict[str, float]
    warnings: List[str]


def extract_number_from_filename(path: Path) -> Optional[int]:
    """Extrai número inicial do arquivo (ex: 01-nome.md -> 1)."""
    match = re.match(r'(\d+)', path.stem)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def evaluate_article(path: Path) -> ArticleReport:
    text = path.read_text(encoding="utf-8")

    title = extract_title(text) or path.stem
    number = extract_number_from_filename(path)

    sections = split_sections(text)
    matched, missing_configs = match_required_sections(sections)

    section_scores: Dict[str, float] = {}
    total_depth = 0.0
    for config in REQUIRED_SECTIONS:
        if config.prefix in matched:
            real_title, content = matched[config.prefix]
            score = assess_section_depth(config, content)
            section_scores[real_title] = score
            total_depth += score

    depth_score = total_depth / len(REQUIRED_SECTIONS) if REQUIRED_SECTIONS else 0.0

    # penalização por seções faltando
    missing_sections_names = [cfg.prefix for cfg in missing_configs]
    depth_penalty = 10.0 * len(missing_sections_names)
    depth_score = max(0.0, depth_score - depth_penalty)

    linkedin_score = assess_linkedin_quality(text)
    formatting_score = assess_formatting(text)
    image_score, image_warnings = assess_images(text, path)

    # score final como média simples dos componentes
    final_score = (depth_score + linkedin_score + formatting_score + image_score) / 4.0

    warnings: List[str] = []
    if missing_sections_names:
        warnings.append(f"Seções faltando: {', '.join(missing_sections_names)}")
    warnings.extend(image_warnings)

    return ArticleReport(
        path=path,
        title=title,
        number=number,
        depth_score=round(depth_score, 1),
        linkedin_score=round(linkedin_score, 1),
        formatting_score=round(formatting_score, 1),
        image_score=round(image_score, 1),
        final_score=round(final_score, 1),
        missing_sections=missing_sections_names,
        section_scores=section_scores,
        warnings=warnings,
    )


# ---------------------------------------------------------------------
# Relatório e CLI
# ---------------------------------------------------------------------


def print_detailed_report(report: ArticleReport) -> None:
    print(f"\n[ARTIGO] {report.title} ({report.path.name})")
    print(f"   Numero: {report.number if report.number is not None else '-'}")
    print(f"   Profundidade: {report.depth_score}/100")
    print(f"   LinkedIn:     {report.linkedin_score}/100")
    print(f"   Formatacao:   {report.formatting_score}/100")
    print(f"   Imagens:      {report.image_score}/100")
    print(f"   Score final:  {report.final_score}/100")

    if report.section_scores:
        print("\n   Secoes avaliadas:")
        for sec_title, score in report.section_scores.items():
            print(f"   - {sec_title}: {score:.1f}/100")

    if report.warnings:
        print("\n   Avisos:")
        for w in report.warnings:
            print(f"   - AVISO: {w}")


def print_summary_table(reports: List[ArticleReport]) -> None:
    print("\n" + "─" * 80)
    print(f"{'Artigo':<32} {'Prof.':>7} {'LinkedIn':>9} {'Format.':>9} {'Img':>7} {'Final':>8}")
    print("─" * 80)
    for r in sorted(reports, key=lambda x: (x.number is None, x.number or 0)):
        label = f"{(r.number or 0):02d} - {r.title[:20]}"
        print(f"{label:<32} {r.depth_score:>7.1f} {r.linkedin_score:>9.1f} {r.formatting_score:>9.1f} {r.image_score:>7.1f} {r.final_score:>8.1f}")
    print("─" * 80)
    avg = sum(r.final_score for r in reports) / len(reports) if reports else 0.0
    print(f"{'MÉDIA':<32} {'':>7} {'':>9} {'':>9} {'':>7} {avg:>8.1f}")
    print("─" * 80)


def main() -> None:
    # Fix encoding issues on Windows
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    if len(sys.argv) < 2:
        print("Uso: python validate-article-guide.py path/para/pasta_com_artigos")
        sys.exit(1)

    root = Path(sys.argv[1]).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"Erro: diretório '{root}' não encontrado ou não é um diretório.")
        sys.exit(1)

    md_files = sorted(root.glob("*.md"))
    if not md_files:
        print(f"Nenhum arquivo .md encontrado em {root}")
        sys.exit(0)

    reports: List[ArticleReport] = []
    for md in md_files:
        report = evaluate_article(md)
        print_detailed_report(report)
        reports.append(report)

    print_summary_table(reports)
    print("\n✅ Validação concluída.")


if __name__ == "__main__":
    main()
