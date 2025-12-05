"""
Gerador de imagens profissionais para o Artigo 02 - Prompt Engineering
Usa matplotlib e PIL para criar diagramas técnicos de alta qualidade
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
import numpy as np
from pathlib import Path

# Paleta de cores profissional
COLORS = {
    'azul': '#2C5282',
    'verde': '#38A169',
    'vermelho': '#E53E3E',
    'cinza': '#718096',
    'cinza_claro': '#E2E8F0',
    'branco': '#FFFFFF',
    'amarelo': '#ECC94B'
}

# Configuração global
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['font.size'] = 12

def create_figura1():
    """Figura 1: Metodologia PACE aplicada a Prompt Engineering"""
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # Título
    ax.text(7, 5.5, 'Metodologia PACE para Prompt Engineering', 
            ha='center', va='top', fontsize=18, fontweight='bold', color=COLORS['azul'])
    
    # Definir posições das caixas
    boxes = [
        {'x': 1, 'title': 'P - Persona', 'icon': '👤', 'text': 'Você é um agente\nde suporte sênior...'},
        {'x': 4.5, 'title': 'A - Approach', 'icon': '⚙️', 'text': 'Cliente insatisfeito +\nPolíticas da empresa'},
        {'x': 8, 'title': 'C - Content', 'icon': '✓', 'text': 'Analise → Identifique\n→ Gere resposta'},
        {'x': 11.5, 'title': 'E - Example', 'icon': '📄', 'text': 'Formato de saída +\nDelimitadores'}
    ]
    
    colors_sequence = [COLORS['azul'], COLORS['verde'], COLORS['cinza'], COLORS['amarelo']]
    
    for i, box in enumerate(boxes):
        # Caixa principal
        rect = FancyBboxPatch((box['x'], 1.5), 2.2, 2.8, 
                              boxstyle="round,pad=0.1", 
                              edgecolor=colors_sequence[i], 
                              facecolor=COLORS['cinza_claro'],
                              linewidth=3)
        ax.add_patch(rect)
        
        # Ícone
        ax.text(box['x'] + 1.1, 3.8, box['icon'], 
                ha='center', va='center', fontsize=28)
        
        # Título
        ax.text(box['x'] + 1.1, 3.2, box['title'], 
                ha='center', va='center', fontsize=13, fontweight='bold',
                color=colors_sequence[i])
        
        # Texto descritivo
        ax.text(box['x'] + 1.1, 2.3, box['text'], 
                ha='center', va='center', fontsize=9, 
                color=COLORS['cinza'], multialignment='center')
        
        # Seta conectando caixas (exceto a última)
        if i < len(boxes) - 1:
            arrow = FancyArrowPatch((box['x'] + 2.3, 2.9), 
                                   (boxes[i+1]['x'] - 0.1, 2.9),
                                   arrowstyle='->', mutation_scale=25, 
                                   linewidth=2.5, color=COLORS['cinza'])
            ax.add_patch(arrow)
    
    # Rodapé
    ax.text(7, 0.5, 'Estrutura para prompts robustos e previsíveis', 
            ha='center', va='center', fontsize=11, 
            color=COLORS['cinza'], style='italic')
    
    plt.tight_layout()
    output_path = Path(__file__).parent / 'figura1.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ Figura 1 criada: {output_path}")


def create_figura2():
    """Figura 2: Evolução de Prompt Ingênuo para Prompt Estruturado"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    
    # Configurar ambos os eixos
    for ax in [ax1, ax2]:
        ax.set_xlim(0, 6)
        ax.set_ylim(0, 8)
        ax.axis('off')
    
    # LADO ESQUERDO - Prompt Ingênuo (❌)
    ax1.text(3, 7.5, '❌ Prompt Ingênuo', ha='center', va='top', 
             fontsize=16, fontweight='bold', color=COLORS['vermelho'])
    
    # Caixa de texto do prompt
    rect1 = FancyBboxPatch((0.5, 4.5), 5, 2.5, 
                          boxstyle="round,pad=0.15", 
                          edgecolor=COLORS['vermelho'], 
                          facecolor='#FFF5F5',
                          linewidth=2)
    ax1.add_patch(rect1)
    
    ax1.text(3, 6, '"Responda a reclamação\ndeste cliente..."', 
             ha='center', va='center', fontsize=11, 
             color=COLORS['cinza'], style='italic')
    
    # Ícone de alerta
    ax1.text(3, 3.5, '⚠️', ha='center', va='center', fontsize=40)
    
    # Problemas
    problems = [
        '• Promete reembolso sem autorização',
        '• Tom inconsistente',
        '• Sem guardrails'
    ]
    
    for i, problem in enumerate(problems):
        ax1.text(0.8, 2.5 - i*0.6, problem, 
                ha='left', va='center', fontsize=10, 
                color=COLORS['vermelho'])
    
    # LADO DIREITO - Prompt Estruturado (✅)
    ax2.text(3, 7.5, '✅ Prompt Estruturado (PACE)', ha='center', va='top', 
             fontsize=16, fontweight='bold', color=COLORS['verde'])
    
    # Blocos PACE
    pace_blocks = [
        {'y': 6.5, 'label': 'Persona', 'color': COLORS['azul']},
        {'y': 5.7, 'label': 'Approach', 'color': COLORS['verde']},
        {'y': 4.9, 'label': 'Content', 'color': COLORS['cinza']},
        {'y': 4.1, 'label': 'Examples', 'color': COLORS['amarelo']}
    ]
    
    for block in pace_blocks:
        rect = Rectangle((0.5, block['y']), 5, 0.6, 
                        edgecolor=block['color'], 
                        facecolor=COLORS['cinza_claro'],
                        linewidth=2)
        ax2.add_patch(rect)
        ax2.text(1, block['y'] + 0.3, block['label'], 
                ha='left', va='center', fontsize=10, 
                fontweight='bold', color=block['color'])
    
    # Ícone de sucesso
    ax2.text(3, 3, '✓', ha='center', va='center', fontsize=50, 
             color=COLORS['verde'])
    
    # Benefícios
    benefits = [
        '• Comportamento previsível',
        '• Respeita políticas',
        '• Tom profissional'
    ]
    
    for i, benefit in enumerate(benefits):
        ax2.text(0.8, 2 - i*0.6, benefit, 
                ha='left', va='center', fontsize=10, 
                color=COLORS['verde'])
    
    plt.tight_layout()
    output_path = Path(__file__).parent / 'figura2.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ Figura 2 criada: {output_path}")


def create_figura3():
    """Figura 3: Principais riscos em Prompt Engineering e suas mitigações"""
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Título
    ax.text(7, 7.5, 'Riscos e Mitigações em Prompt Engineering', 
            ha='center', va='top', fontsize=18, fontweight='bold', color=COLORS['azul'])
    
    # LADO ESQUERDO - RISCOS
    ax.text(3.5, 6.5, '🚨 RISCOS', ha='center', va='center', 
            fontsize=15, fontweight='bold', color=COLORS['vermelho'])
    
    risks = [
        {'title': 'Prompt Injection', 'icon': '🔓', 
         'desc': 'Usuário tenta sobrescrever\ninstruções do sistema'},
        {'title': 'Ambiguidade de Tom', 'icon': '❓', 
         'desc': 'Respostas inconsistentes\nou inadequadas'}
    ]
    
    y_pos = 5
    for risk in risks:
        # Caixa de risco
        rect = FancyBboxPatch((0.5, y_pos - 0.8), 6, 1.8, 
                             boxstyle="round,pad=0.1", 
                             edgecolor=COLORS['vermelho'], 
                             facecolor='#FFF5F5',
                             linewidth=2)
        ax.add_patch(rect)
        
        ax.text(1.2, y_pos + 0.3, risk['icon'], 
                ha='center', va='center', fontsize=24)
        ax.text(2.5, y_pos + 0.4, risk['title'], 
                ha='left', va='center', fontsize=12, 
                fontweight='bold', color=COLORS['vermelho'])
        ax.text(2.5, y_pos - 0.2, risk['desc'], 
                ha='left', va='center', fontsize=9, 
                color=COLORS['cinza'])
        
        y_pos -= 2.5
    
    # Setas de mitigação
    for y in [5, 2.5]:
        arrow = FancyArrowPatch((6.8, y), (7.5, y),
                               arrowstyle='->', mutation_scale=30, 
                               linewidth=3, color=COLORS['cinza'])
        ax.add_patch(arrow)
    
    # LADO DIREITO - MITIGAÇÕES
    ax.text(10.5, 6.5, '✅ MITIGAÇÕES', ha='center', va='center', 
            fontsize=15, fontweight='bold', color=COLORS['verde'])
    
    mitigations = [
        {'title': 'Delimitadores Claros', 'icon': '###', 
         'desc': 'Separar instruções\nde dados do usuário'},
        {'title': 'Instruções Específicas', 'icon': '📋', 
         'desc': 'Tom empático, profissional,\nsem informalidade'}
    ]
    
    y_pos = 5
    for mitigation in mitigations:
        # Caixa de mitigação
        rect = FancyBboxPatch((7.5, y_pos - 0.8), 6, 1.8, 
                             boxstyle="round,pad=0.1", 
                             edgecolor=COLORS['verde'], 
                             facecolor='#F0FFF4',
                             linewidth=2)
        ax.add_patch(rect)
        
        ax.text(8.2, y_pos + 0.3, mitigation['icon'], 
                ha='center', va='center', fontsize=20, 
                fontweight='bold', color=COLORS['verde'])
        ax.text(9.5, y_pos + 0.4, mitigation['title'], 
                ha='left', va='center', fontsize=12, 
                fontweight='bold', color=COLORS['verde'])
        ax.text(9.5, y_pos - 0.2, mitigation['desc'], 
                ha='left', va='center', fontsize=9, 
                color=COLORS['cinza'])
        
        y_pos -= 2.5
    
    plt.tight_layout()
    output_path = Path(__file__).parent / 'figura3.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ Figura 3 criada: {output_path}")


def create_figura4():
    """Figura 4: Dashboard de métricas para avaliar qualidade de prompts"""
    fig = plt.figure(figsize=(14, 8))
    
    # Título principal
    fig.text(0.5, 0.95, 'Dashboard de Qualidade de Prompts', 
             ha='center', va='top', fontsize=20, fontweight='bold', 
             color=COLORS['azul'])
    
    # Grid de 3 colunas para KPIs
    ax1 = plt.subplot(3, 3, 1)
    ax2 = plt.subplot(3, 3, 2)
    ax3 = plt.subplot(3, 3, 3)
    
    # KPI 1: Taxa de Recontato
    ax1.axis('off')
    ax1.text(0.5, 0.8, '📊', ha='center', va='center', fontsize=40, transform=ax1.transAxes)
    ax1.text(0.5, 0.5, 'Taxa de Recontato', ha='center', va='center', 
             fontsize=12, fontweight='bold', color=COLORS['cinza'], transform=ax1.transAxes)
    ax1.text(0.5, 0.25, '15%', ha='center', va='center', 
             fontsize=28, fontweight='bold', color=COLORS['verde'], transform=ax1.transAxes)
    ax1.text(0.5, 0.05, '↓ 5% vs mês anterior', ha='center', va='center', 
             fontsize=9, color=COLORS['verde'], transform=ax1.transAxes)
    
    # KPI 2: Aderência à Política
    ax2.axis('off')
    # Gauge simples
    theta = np.linspace(0, np.pi, 100)
    r = 0.3
    x_gauge = r * np.cos(theta) + 0.5
    y_gauge = r * np.sin(theta) + 0.3
    ax2.plot(x_gauge, y_gauge, linewidth=8, color=COLORS['cinza_claro'], transform=ax2.transAxes)
    
    # Preenchimento até 94%
    theta_fill = np.linspace(0, np.pi * 0.94, 100)
    x_fill = r * np.cos(theta_fill) + 0.5
    y_fill = r * np.sin(theta_fill) + 0.3
    ax2.plot(x_fill, y_fill, linewidth=8, color=COLORS['verde'], transform=ax2.transAxes)
    
    ax2.text(0.5, 0.65, 'Aderência à Política', ha='center', va='center', 
             fontsize=12, fontweight='bold', color=COLORS['cinza'], transform=ax2.transAxes)
    ax2.text(0.5, 0.15, '94%', ha='center', va='center', 
             fontsize=28, fontweight='bold', color=COLORS['verde'], transform=ax2.transAxes)
    
    # KPI 3: Qualidade de Linguagem
    ax3.axis('off')
    ax3.text(0.5, 0.8, '💬', ha='center', va='center', fontsize=40, transform=ax3.transAxes)
    ax3.text(0.5, 0.5, 'Qualidade de Linguagem', ha='center', va='center', 
             fontsize=12, fontweight='bold', color=COLORS['cinza'], transform=ax3.transAxes)
    ax3.text(0.5, 0.25, '★★★★☆', ha='center', va='center', 
             fontsize=22, color=COLORS['amarelo'], transform=ax3.transAxes)
    ax3.text(0.5, 0.05, '4.2 / 5.0', ha='center', va='center', 
             fontsize=11, fontweight='bold', color=COLORS['cinza'], transform=ax3.transAxes)
    
    # Tabela Golden Dataset (parte inferior)
    ax_table = plt.subplot(3, 1, (2, 3))
    ax_table.axis('off')
    
    ax_table.text(0.5, 0.95, 'Golden Dataset - Resultados de Validação', 
                 ha='center', va='top', fontsize=14, fontweight='bold', 
                 color=COLORS['azul'], transform=ax_table.transAxes)
    
    # Cabeçalhos da tabela
    headers = ['Caso de Teste', 'Status', 'Aderência', 'Observações']
    col_widths = [0.3, 0.15, 0.15, 0.4]
    x_start = 0.05
    
    for i, (header, width) in enumerate(zip(headers, col_widths)):
        ax_table.text(x_start + sum(col_widths[:i]) + width/2, 0.85, header, 
                     ha='center', va='center', fontsize=11, fontweight='bold',
                     color=COLORS['azul'], transform=ax_table.transAxes)
    
    # Dados da tabela
    rows = [
        {'caso': 'Pizza fria', 'status': '✅ Pass', 'ader': '100%', 'obs': 'Tom empático mantido', 'color': COLORS['verde']},
        {'caso': 'Motoboy rude', 'status': '✅ Pass', 'ader': '100%', 'obs': 'Política respeitada', 'color': COLORS['verde']},
        {'caso': 'Pedido errado', 'status': '⚠️ Review', 'ader': '85%', 'obs': 'Ambiguidade no reembolso', 'color': COLORS['amarelo']},
        {'caso': 'Atraso 60min', 'status': '✅ Pass', 'ader': '98%', 'obs': 'Escalação correta', 'color': COLORS['verde']},
    ]
    
    y_pos = 0.75
    for row in rows:
        # Fundo da linha
        rect = Rectangle((0.03, y_pos - 0.04), 0.94, 0.08, 
                        facecolor=COLORS['cinza_claro'], 
                        edgecolor=COLORS['cinza'], linewidth=0.5,
                        transform=ax_table.transAxes)
        ax_table.add_patch(rect)
        
        # Dados
        ax_table.text(x_start + col_widths[0]/2, y_pos, row['caso'], 
                     ha='center', va='center', fontsize=10, 
                     color=COLORS['cinza'], transform=ax_table.transAxes)
        ax_table.text(x_start + col_widths[0] + col_widths[1]/2, y_pos, row['status'], 
                     ha='center', va='center', fontsize=10, fontweight='bold',
                     color=row['color'], transform=ax_table.transAxes)
        ax_table.text(x_start + col_widths[0] + col_widths[1] + col_widths[2]/2, y_pos, row['ader'], 
                     ha='center', va='center', fontsize=10, fontweight='bold',
                     color=row['color'], transform=ax_table.transAxes)
        ax_table.text(x_start + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3]/2, y_pos, row['obs'], 
                     ha='center', va='center', fontsize=9, style='italic',
                     color=COLORS['cinza'], transform=ax_table.transAxes)
        
        y_pos -= 0.12
    
    plt.tight_layout()
    output_path = Path(__file__).parent / 'figura4.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ Figura 4 criada: {output_path}")


def main():
    """Gera todas as figuras do artigo 02"""
    print("🎨 Gerando imagens para o Artigo 02 - Prompt Engineering\n")
    
    try:
        create_figura1()
        create_figura2()
        create_figura3()
        create_figura4()
        
        print("\n✅ Todas as imagens foram geradas com sucesso!")
        print(f"📁 Local: {Path(__file__).parent}")
        
    except Exception as e:
        print(f"❌ Erro ao gerar imagens: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
