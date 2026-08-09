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

* ### [9Router](https://9router.com/) ([repo](https://github.com/decolua/9router))
  * **Descrição:** Roteador de IA gratuito e open-source (mesma proposta do `OmniRoute` acima) que unifica o acesso a mais de 40 provedores e 100+ modelos por trás de um único endpoint local. Conecta ferramentas como Claude Code, Cursor, Codex, Cline, Copilot e Gemini CLI a modelos comerciais/gratuitos, com fallback automático ao atingir limites de taxa, tradução entre formatos de API (OpenAI ↔ Claude ↔ Gemini) e compressão de tokens (economia de ~20-40% em saídas de `git diff`, `grep`, `ls`, `tree`, etc.).

* ### [ruvnet/ruflo](https://github.com/ruvnet/ruflo)
  * **Descrição:** Framework open-source para orquestração de múltiplos agentes de IA (*swarm intelligence* e *agentic workflows*). Permite criar fluxos de trabalho colaborativos e distribuídos entre assistentes de IA.

* ### [affaan-m/ECC](https://github.com/affaan-m/ECC)
  * **Descrição:** Framework open-source (MIT) que dá a agentes de codificação um sistema de engenharia coordenado, com o ciclo `plan -> test -> implement -> review -> verify -> remember -> improve`, 67 agentes especializados, 284 skills reutilizáveis, hooks/memória para aprendizado contínuo e o scanner de segurança AgentShield. Nativo para Claude Code, com adaptadores para Codex, Cursor, OpenCode, Gemini, Zed e GitHub Copilot.
  * **Comando `/ecc:xxx`:** o prefixo vem do `name: "ecc"` em `.claude-plugin/plugin.json` — basta criar `commands/<nome>.md` com `description:` no frontmatter para o comando surgir automaticamente, sem registro manual.
  * **Skills:** instale por perfil (`--profile minimal|core|full`), por nome (`--skills tdd-workflow,security-review`) ou peça sugestão (`npx ecc-universal consult "<necessidade>"`).
  * **Comando ≠ skill — o comando fixa quais skills carregar, a skill fica genérica:** o `.md` do comando não faz o trabalho pesado, mas também não delega a decisão de "quais skills usar" — essa lista fica fixa nele, para cada comando poder combinar um pacote diferente da mesma skill reutilizável. 
  
  Estrutura:

    ```
    .claude/
    ├── commands/
    │   └── ecc/
    │       └── spec.md
    └── skills/
        ├── api-design/
        ├── security-review/
        └── backend-patterns/        (ou frontend-patterns/)
    ```

  Exemplo mínimo, um `/ecc:spec` que gera `SPEC.md`:

    ```
    commands/ecc/spec.md
    ---
    description: Cria uma especificação técnica para uma feature
    ---

    # Technical Specification

    Você está criando uma especificação técnica para a feature solicitada pelo usuário.

    Feature solicitada:

    $ARGUMENTS

    Carregue e use estas skills antes de continuar:
    - api-design
    - backend-patterns / frontend-patterns
    - security-review
    - tdd-workflow

    Depois, use a skill `spec` para produzir a especificação.

    Pedido do usuário:
    $ARGUMENTS

    Considere obrigatoriamente:

    1. Arquitetura existente
    2. Padrões utilizados no projeto
    3. APIs existentes
    4. Modelos de dados
    5. Segurança
    6. Testes
    7. Impacto em frontend e backend

    ## Resultado

    Crie uma especificação técnica contendo:

    ### 1. Contexto

    ### 2. Objetivo

    ### 3. Arquitetura
    ```

    Obs: importante é usar o $ARGUMENTS e a parte de quais skills devem ser carregada, todo resto pode ser comportamento extra desse comando.

    Uso: `/ecc:spec Autenticação OAuth com Google` — o texto após o comando chega como `$ARGUMENTS`; as skills carregadas vêm sempre do comando, não da skill `spec`.

* ### [teamchong/pxpipe](https://github.com/teamchong/pxpipe)
  * **Descrição:** Ferramenta de otimização de context window (Image to Prompt). Converte grandes volumes de texto (system prompts, documentação de ferramentas e histórico antigo) em imagens PNG comprimidas. Como os modelos de visão cobram um valor fixo de tokens por imagem, reduz o custo total de tokens de entrada em 50% a 70%.

* ### [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
  * **Descrição:** Framework de OCR (reconhecimento óptico de caracteres) open-source da Baidu. Permite extrair texto de imagens e documentos, útil para alimentar agentes de IA com conteúdo digitalizado.

* ### [ruvnet/ruview](https://github.com/ruvnet/ruview)
  * **Descrição:** Plataforma de sensoriamento via WiFi que transforma sinais de rádio em inteligência espacial em tempo real, detectando presença, sinais vitais (respiração e batimentos) e postura corporal sem câmeras ou wearables. Usa nós ESP32 de baixo custo, redes neurais para reconhecimento de atividades/quedas, e integra-se a Home Assistant, Apple Home, Google Home e Alexa via protocolo Matter.

* ### [anthropics/claude-plugins-official (claude-code-setup)](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-code-setup)
  * **Descrição:** Plugin oficial da Anthropic que analisa a codebase do projeto e recomenda automações sob medida para o Claude Code — servidores MCP, Skills, Hooks, Subagents e Slash Commands. Funciona em modo *read-only* (não altera arquivos), servindo como um assistente de onboarding e otimização de workflow.

* ### [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)
  * **Descrição:** Conjunto de diretrizes de comportamento (via `CLAUDE.md`/plugin) inspiradas nas observações de Andrej Karpathy sobre erros comuns de LLMs ao programar. Ensina o agente a pensar antes de codificar, evitar superengenharia, fazer mudanças cirúrgicas (só o necessário) e definir critérios de sucesso verificáveis antes de executar.

* ### [juliusbrussee/caveman](https://github.com/juliusbrussee/caveman)
  * **Descrição:** Skill/plugin que faz o agente de IA se comunicar de forma ultra-comprimida ("fala de caveman"), reduzindo em até 65% os tokens de saída em texto corrido sem perder precisão técnica. Possui níveis de intensidade ajustáveis (lite/full/ultra/wenyan), comandos para commits e revisões de PR comprimidos, e compressão de arquivos de memória/contexto.

* ### [dietrichgebert/ponytail](https://github.com/dietrichgebert/ponytail)
  * **Descrição:** Plugin que faz o agente pensar como "o dev sênior mais preguiçoso da sala", aplicando uma escada de decisão (reutilizar → stdlib → recursos nativos → dependências existentes → solução mínima) antes de escrever qualquer código novo. Resulta em ~54% menos código gerado, mantendo segurança e validação.

* ### [getagentseal/codeburn](https://github.com/getagentseal/codeburn)
  * **Descrição:** Ferramenta open-source, local e gratuita para rastrear gastos com tokens de IA e seus custos associados, mostrando onde o orçamento é consumido por modelo, projeto e tipo de tarefa. Monitora 36 ferramentas diferentes (Claude Code, Cursor, Codex, Gemini, Grok, etc.) a partir dos arquivos de sessão já presentes na máquina, com dashboard no terminal, painel web com gráficos e app de menu para macOS. Opera 100% offline — nenhum dado sai da máquina — e permite definir limites de gasto em sessões do Claude Code.

#### 🔍 Comparativo: andrej-karpathy-skills vs. caveman vs. ponytail

Os três são plugins/skills comportamentais para agentes de IA (Claude Code, Cursor, etc.), mas cada um otimiza uma dimensão diferente do trabalho do agente.

| Critério | [andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | [caveman](https://github.com/juliusbrussee/caveman) | [ponytail](https://github.com/dietrichgebert/ponytail) |
| :--- | :--- | :--- | :--- |
| **Foco principal** | Qualidade do raciocínio e do código (evitar suposições, escopo e complexidade indevidos) | Redução de tokens na **comunicação/prosa** do agente | Redução de **quantidade de código** gerado (minimalismo) |
| **O que otimiza** | Correção e disciplina de implementação | Custo de API e velocidade de resposta em texto | Manutenibilidade e superfície de código (menos linhas p/ manter/revisar) |
| **Melhor quando** | Você quer um agente mais criterioso, que pergunta antes de assumir e não "invade" código fora do escopo | Você roda muitas sessões/agentes e quer cortar custo de tokens em explicações e respostas longas | Você quer evitar reinvenção de rodas e código inchado, priorizando stdlib/deps existentes |
| **Não resolve** | Não reduz tokens nem volume de código gerado | Não impede superengenharia nem código desnecessário | Não trata verbosidade de texto/explicações |
| **Sobreposição** | Complementa bem os outros dois (raciocínio + eficiência) | Pode ser combinado com ponytail (tokens de texto + tokens de código) | Pode ser combinado com caveman (código enxuto + prosa enxuta) |
| **Quando usar juntos** | Base recomendada para qualquer projeto | Projetos com custo de API alto ou sessões muito longas | Projetos legados/grandes onde cada linha nova tem custo de manutenção |

**Recomendação prática:** os três não são mutuamente exclusivos — `andrej-karpathy-skills` melhora *como* o agente pensa, `ponytail` reduz *quanto código* ele escreve, e `caveman` reduz *quantos tokens* ele gasta explicando o que fez. Usá-los em conjunto costuma trazer o melhor resultado: raciocínio disciplinado + código mínimo + comunicação enxuta.