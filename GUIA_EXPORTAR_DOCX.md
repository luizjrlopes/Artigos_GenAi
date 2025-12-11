# Como Adicionar Botão de Exportar para DOCX

## 1️⃣ Adicione o Script no `<head>` do HTML

```html
<head>
  <!-- ... outros scripts ... -->
  <script src="scripts/export-to-docx.js"></script>
</head>
```

## 2️⃣ Adicione o Botão no Header (perto da logo)

```html
<header class="bg-white border-b border-gray-200 fixed w-full top-0 z-50">
  <div
    class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between"
  >
    <a
      href="index.html"
      class="flex items-center space-x-3 hover:opacity-80 transition-opacity cursor-pointer"
    >
      <div class="bg-brand-600 text-white p-2 rounded-lg">
        <i class="fas fa-cubes"></i>
      </div>
      <h1 class="text-xl font-bold text-gray-900">LLM Product Engineering</h1>
    </a>

    <!-- BOTÃO DE EXPORTAR AQUI -->
    <div class="flex items-center gap-4">
      <div class="hidden md:block text-sm text-gray-500">
        Módulo 1: Fundamentos e Estratégias de Customização
      </div>
      <button
        id="export-docx-btn"
        title="Exportar artigo como DOCX"
        class="hidden md:flex items-center gap-2 px-4 py-2 bg-brand-50 hover:bg-brand-100 text-brand-700 rounded-lg transition-colors"
      >
        <i class="fas fa-download"></i>
        <span class="text-sm font-medium">Exportar DOCX</span>
      </button>
    </div>
  </div>
</header>
```

## 3️⃣ Versão Compacta para Mobile

Se preferir um botão menor para mobile, use um ícone:

```html
<button
  id="export-docx-btn"
  title="Exportar artigo como DOCX"
  class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
>
  <i class="fas fa-file-word text-brand-600"></i>
</button>
```

---

## 🎯 Resultado Final

O botão aparecerá assim:

```
[Logo] LLM Product Engineering    [Módulo Info]    [Exportar DOCX ↓]
```

Quando clicado:

1. Coleta todo o conteúdo do artigo (`<main>`)
2. Remove navegação e elementos desnecessários
3. Gera um arquivo `.docx` com:
   - ✅ Títulos e hierarquia preservada
   - ✅ Parágrafos formatados
   - ✅ Tabelas
   - ✅ Cores (compatível com Word)
4. Download automático com nome do artigo

---

## 📝 Opções de Personalização

### A. Se você quer preservar **mais CSS** (cores, fontes):

Troque no `export-to-docx.js` a função chamada de:

```javascript
exporter.exportWithHtmlDocx();
```

Para:

```javascript
exporter.exportToDocxAdvanced();
```

### B. Se você quer um **botão flutuante** no canto:

```html
<button
  id="export-docx-btn"
  class="fixed bottom-8 right-8 w-14 h-14 bg-brand-600 hover:bg-brand-700 text-white rounded-full shadow-lg flex items-center justify-center transition-transform hover:scale-110"
  title="Exportar como DOCX"
>
  <i class="fas fa-file-word text-xl"></i>
</button>
```

### C. Se você quer **customizar o nome do arquivo**:

Adicione um atributo `data-filename` no botão:

```html
<button
  id="export-docx-btn"
  data-filename="Artigo-01-Do-Modelo-ao-Produto"
  class="..."
></button>
```

---

## 🚀 Próximos Passos

1. **Copie o script** `scripts/export-to-docx.js` para todos os artigos HTML
2. **Adicione o botão** no header de cada artigo
3. **Teste** clicando no botão
4. **Customize cores/estilos** se necessário

---

## 📦 Dependências (via CDN - sem instalação necessária)

- `html-docx-js` - Converte HTML para DOCX
- Bibliotecas carregadas automaticamente no primeiro clique

**Nenhuma dependência NPM necessária!** Tudo funciona via CDN.

---

## ⚠️ Troubleshooting

| Problema             | Solução                                                                  |
| -------------------- | ------------------------------------------------------------------------ |
| Botão não funciona   | Verifique se `export-to-docx.js` foi carregado (abra DevTools → Console) |
| Arquivo não baixa    | Verifique extensão do browser (algumas bloqueiam downloads automáticos)  |
| Formatação perdida   | Use `exportToDocxAdvanced()` ao invés de `exportWithHtmlDocx()`          |
| Arquivo muito grande | Remova imagens pesadas do HTML antes de exportar                         |

---

## 🎨 Customização Visual

Você pode estilizar o botão como preferir. Exemplos:

### Botão com Ícone e Texto

```html
<button class="px-4 py-2 bg-brand-600 text-white rounded hover:bg-brand-700">
  <i class="fas fa-download mr-2"></i> Exportar
</button>
```

### Botão Minimalista

```html
<button class="text-gray-500 hover:text-brand-600" title="Exportar DOCX">
  <i class="fas fa-file-word text-lg"></i>
</button>
```

### Botão com Menu Dropdown

```html
<div class="relative group">
  <button class="px-4 py-2 bg-brand-50 hover:bg-brand-100 rounded">
    <i class="fas fa-download"></i> Exportar
  </button>
  <div
    class="hidden group-hover:block absolute right-0 mt-2 w-48 bg-white shadow-lg rounded"
  >
    <button
      id="export-docx-btn"
      class="block w-full text-left px-4 py-2 hover:bg-gray-50"
    >
      📄 Exportar como DOCX
    </button>
    <button
      id="export-pdf-btn"
      class="block w-full text-left px-4 py-2 hover:bg-gray-50"
    >
      📕 Exportar como PDF
    </button>
  </div>
</div>
```
