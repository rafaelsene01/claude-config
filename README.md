# Curadoria de Recursos para IA: MCPs, Skills e Ferramentas

## 🔌 MCP (Model Context Protocol)

Servidores que implementam o protocolo MCP para expandir as capacidades de assistentes de IA (Cursor, Claude Code, Windsurf, VS Code).

* ### [21st-dev/magic-mcp](https://github.com/21st-dev/magic-mcp)
  * **Descrição:** Servidor MCP oficial da plataforma *21st.dev* (substituto do antigo Magic MCP). Permite buscar em um catálogo de mais de 10.000 componentes React e Tailwind, gerar novas UIs com IA e integrar diretamente no editor de código.

* ### [Jpisnice/shadcn-ui-mcp-server](https://github.com/Jpisnice/shadcn-ui-mcp-server)
  * **Descrição:** Servidor MCP dedicado ao ecossistema `shadcn/ui`. Permite que a IA busque componentes, visualize documentação/código e instale componentes `shadcn/ui` diretamente no projeto.

* ### [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp)
  * **Descrição:** Servidor MCP oficial desenvolvido pela equipe do Chrome DevTools. Permite que assistentes de IA se conectem ao navegador para inspecionar o DOM, analisar a rede, auditar acessibilidade e depurar a aplicação em tempo real.

* ### [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)
  * **Descrição:** Servidor MCP que transforma bases de dados, arquivos e dados não estruturados em grafos de conhecimento (*Knowledge Graphs*). Melhora significativamente a recuperação de contexto (RAG) para agentes de IA, permitindo mapear relações complexas entre informações.

---

## 🎨 Skills para IA (Prompt & Design Guidelines)

Habilidades e pacotes de instruções projetados para calibrar e aprimorar o comportamento de modelos de linguagem e agentes.

### 🖌️ Skills de Frontend, UI & UX Design

* ### [leonxlnx/taste-skill](https://github.com/leonxlnx/taste-skill)
  * **Descrição:** Skill focada em "bom gosto visual" e estética de UI. Fornece aos agentes orientações sobre refinamento visual, escolha de cores, alinhamentos e tom de design elegante para evitar UIs genéricas.

* ### [pbakaus/impeccable](https://github.com/pbakaus/impeccable)
  * **Descrição:** Coleção de diretrizes de engenharia frontend e design de Paul Bakaus. Ensina IAs a aplicar práticas rigorosas de UX, acessibilidade, responsividade *Mobile-First* e padrões modernos de CSS.

* ### [emilkowalski/skills](https://github.com/emilkowalski/skills)
  * **Descrição:** Criada por Emil Kowalski (especialista em UI/animação e criador do Sonner). Foca em micro-interações, animações fluídas (Framer Motion / CSS), acessibilidade e detalhes de acabamento de altíssimo nível.

* ### [vercel-labs/agent-skills (web-design-guidelines)](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines)
  * **Descrição:** Skill mantida pela Vercel Labs com diretrizes de Web Design para IAs. Foca na construção de interfaces modernas em React/Next.js, hierarquia visual, espaçamento e padronização.

* ### [anthropics/skills (frontend-design)](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md)
  * **Descrição:** Skill oficial da Anthropic para design de frontend. Orienta o Claude a criar interfaces web elegantes, utilizáveis, modernas e responsivas, superando padrões clichês gerados por IA.

### 🧠 Skills de Conhecimento, Pesquisa & Engenharia de Prompts

* ### [PleasePrompto/notebooklm-skill](https://github.com/PleasePrompto/notebooklm-skill)
  * **Descrição:** Skill focada em emular a metodologia do NotebookLM da Google. Orienta o modelo de IA a atuar como um especialista em síntese, curadoria e análise profunda de documentos, organizando fontes e gerando resumos estruturados de alto valor factual.

---

## 🛠️ Outros (Segurança, Sandbox, Roteamento & Otimizações)

* ### [Artigo TabNews: Confiei no Claude Code no piloto automático...](https://www.tabnews.com.br/kenimo49/confiei-no-claude-code-no-piloto-automatico-e-o-shai-hulud-quase-entrou-5-permissoes-que-reduzi-hoje)
  * **Descrição:** Artigo por Ken Imoto relatando riscos de segurança ao usar o Claude Code no modo *Auto* (piloto automático) contra ataques de *prompt-injection* e pacotes npm maliciosos (como o worm Shai-Hulud). Apresenta 5 regras práticas de permissão no `settings.json` para proteger credenciais e o sistema local.

* ### [akitaonrails/ai-jail](https://github.com/akitaonrails/ai-jail)
  * **Descrição:** Desenvolvido por Fabio Akita, é um wrapper de segurança/sandbox multi-OS (usando `bubblewrap` no Linux e `sandbox-exec` no macOS). Restringe o acesso do Claude Code e outros agentes de IA apenas às pastas do projeto, isolando arquivos sensíveis como `~/.ssh` e `.env`.

* ### [diegosouzapw/OmniRoute](https://github.com/diegosouzapw/OmniRoute)
  * **Descrição:** Roteador inteligente de requisições LLM. Permite gerenciar múltiplos provedores e modelos de IA (OpenAI, Anthropic, Gemini, Ollama, etc.), aplicando estratégias de fallback, balanceamento de carga, monitoramento de custos e controle de latência.

* ### [ruvnet/ruflo](https://github.com/ruvnet/ruflo)
  * **Descrição:** Framework open-source para orquestração de múltiplos agentes de IA (*swarm intelligence* e *agentic workflows*). Permite criar fluxos de trabalho colaborativos e distribuídos entre assistentes de IA.

* ### [teamchong/pxpipe](https://github.com/teamchong/pxpipe)
  * **Descrição:** Ferramenta de otimização de context window (Image to Prompt). Converte grandes volumes de texto (system prompts, documentação de ferramentas e histórico antigo) em imagens PNG comprimidas. Como os modelos de visão cobram um valor fixo de tokens por imagem, reduz o custo total de tokens de entrada em 50% a 70%.