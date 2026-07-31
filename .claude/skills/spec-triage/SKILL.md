---
name: spec-triage
description: Varre o conjunto de specs de qualquer projeto, reconcilia a documentação com o que o código realmente diz, inventaria o que está aberto e classifica cada item, e faz ao usuário todas as perguntas que só ele pode responder — gravando cada resposta dentro da spec, para que a execução depois rode sem nenhuma intervenção. Não implementa nada, não roda gate, não dirige o app. Use quando o pedido for "veja o que falta nas specs", "atualize as specs", "o que precisa da minha decisão", "as specs estão certas?", ou antes de qualquer run de spec-loop.
---

# spec-triage — mapear, reconciliar, decidir

Esta skill produz **specs executáveis sem intervenção humana**. É a metade de planejamento de um par:

| Skill | Faz | Não faz |
| --- | --- | --- |
| **spec-triage** (esta) | reconcilia a documentação com o código, inventaria o que está aberto, classifica, pergunta ao usuário e **grava a resposta na spec** | não implementa, não roda gate, não dirige o app |
| **spec-loop** | executa o que a triagem marcou como pronto, com validação adversarial em loop | **nunca pergunta ao usuário**; item que precisa de decisão é estacionado e devolvido para cá |

A fronteira existe por um motivo prático: perguntar é bloqueante, executar não. Misturar os dois faz uma onda de subagents parar porque uma task esbarrou numa dúvida. E perguntar **depois** de o código estar escrito custa o retrabalho do código.

Quem executa esta skill **não edita código**. Edita documentação. Toda leitura pesada do código vai para subagent — o contexto de quem orquestra precisa durar até a última pergunta.

**Esta skill não conhece o seu projeto.** Ela conhece um método. Tudo que for específico — onde ficam as specs, quais são os comandos de gate, qual o idioma da documentação, o que é território compartilhado — é **descoberto na Fase 0**, nunca assumido. Se você é um agente lendo isto e reconhece um nome de arquivo aqui, ele é exemplo, não fato.

---

## Fase 0 — Descobrir o projeto antes de auditá-lo

Nada depois disto funciona sem isto. Levante, na ordem, e anote o que achou:

**1. Onde mora o conjunto de specs.** Procure, nesta ordem, e pare no primeiro que existir:
`.specs/` · `specs/` · `docs/specs/` · `.kiro/specs/` · `spec/` · um diretório apontado pelo `AGENTS.md`/`CLAUDE.md`/`README`.

Dentro dele, identifique os três papéis (os nomes variam; o papel é o que importa):

| Papel | Nomes comuns |
| --- | --- |
| estado vivo — decisões, bloqueios, pendências | `project/STATE.md`, `STATE.md`, `DECISIONS.md`, ADRs em `docs/adr/` |
| escopo e ordem — milestones, fases | `project/ROADMAP.md`, `ROADMAP.md`, `PLAN.md` |
| retrato do código — arquitetura, convenções, testes | `codebase/*`, `docs/architecture/`, `CONVENTIONS.md`, `TESTING.md` |
| por feature — requisitos, desenho, tasks | `features/<nome>/{spec,design,tasks,context}.md` |

**Se não existir conjunto de specs nenhum, pare.** Esta skill faz triagem de specs; ela não as cria do zero. Diga ao usuário que o projeto precisa ser especificado primeiro (a skill `tlc-spec-driven` faz isso) e ofereça-se para rodar aquilo.

**2. Onde as tasks moram — e onde uma decisão fica gravada.** É a pergunta que decide se o contrato da Fase 3 tem endereço. Três casos:

| Caso | Onde a task vive | Onde a decisão do usuário é gravada |
| --- | --- | --- |
| **markdown no repositório** (padrão) | `features/<f>/tasks.md` ou equivalente | no próprio arquivo da feature |
| **rastreador externo** (Jira, Linear, GitHub Issues) | fora do repositório | **também num arquivo do repositório** — ver abaixo |
| **híbrido** | ticket externo referenciando a spec | no repositório, com o ID do ticket ao lado |

⚠️ **Com rastreador externo, a decisão precisa existir dentro do repositório de qualquer forma.** O subagent implementador costuma não ter credencial do rastreador, e mesmo quando tem, ele não vai encontrar o comentário certo na thread. Escolha (ou crie) um arquivo por feature — `context.md`, `decisions.md`, o que o projeto usar — e trate o ticket como espelho, não como fonte. **A fonte é a que o agente consegue ler sem rede e sem credencial.** Anote no perfil qual é o arquivo e como se referencia o ticket.

Anote também se as tasks **declaram os arquivos que tocam**. Se não declaram, a `spec-loop` não consegue montar onda e vai serializar tudo — o que é seguro, mas precisa estar escrito no perfil para ninguém confundir com lentidão inexplicável.

**3. Qual o controle de versão, e qual o comando de revisão.** A `spec-loop` usa isso para saber se a triagem envelheceu:

| VCS | revisão | estado da árvore |
| --- | --- | --- |
| git | `git rev-parse --short HEAD` | `git status --short` |
| mercurial | `hg id -i` | `hg status` |
| svn | `svnversion` | `svn status` |
| **nenhum** | não existe | listagem de arquivos + mtime |

**Sem VCS, o frescor da triagem não é verificável** — anote isso no perfil com todas as letras. A regra passa a ser: a triagem só vale na mesma sessão, e a `spec-loop` recomeça pela triagem em qualquer sessão nova. Um `TRIAGE.md` sem revisão registrada que a `spec-loop` aceite calada é pior que triagem nenhuma: ela executa classificação velha achando que está fresca.

**4. Quais regras o repositório impõe.** Leia `AGENTS.md`, `CLAUDE.md`, `.claude/rules/*`, `CONTRIBUTING.md`. Elas **sobrepõem** qualquer padrão desta skill. Anote em especial:
- exigência de marcador de rastreabilidade nos arquivos (um comentário no topo ligando arquivo → requisito) e o formato exato dele;
- política de commit (esta skill nunca commita por conta própria, mas o projeto pode proibir mais coisas);
- idioma: em que língua se escreve **código/comentários** e em que língua se escreve **documentação**. Podem ser diferentes, e frequentemente são.

**5. Quais são os gates, medidos e não presumidos.** Ache os comandos reais em `package.json`, `Makefile`, `justfile`, `Cargo.toml`, `pyproject.toml`, e principalmente nos workflows de CI — o CI é a definição operacional de "passou". Anote o comando de: build, testes (cada suíte), lint/type-check, e qualquer verificação de geração de artefato.

**Rode cada um agora e anote o número.** Este é o baseline da triagem, e é o único número que você tem direito de escrever em documento nesta run.

⚠️ **Em monorepo, gate é por escopo.** Não colapse `test` de seis pacotes num número só — a soma não falha quando um pacote regride, e ninguém sabe qual comando rodar numa task específica. Anote uma linha por escopo (raiz + cada pacote que tem suíte própria), e no inventário registre **qual escopo cada item toca**. É isso que a `spec-loop` cola no brief do implementador; um brief com o gate do pacote errado produz um "passou" que não significa nada.

**6. Qual o território compartilhado deste projeto.** É o que a `spec-loop` vai usar para não paralelizar duas tasks que colidem. Procure por:

| Padrão | Como se manifesta | Por que colide |
| --- | --- | --- |
| migrações numeradas em sequência | lista/array de migrações, arquivos `NNN_*.sql` | duas com o mesmo número costumam **não** quebrar o build; a segunda só nunca roda |
| arquivos de tradução espelhados | `locales/*.json`, `.po` | precisam de paridade de chave; dois editores geram divergência |
| arquivo gerado a partir de outro | tipos gerados, clientes de API, snapshots | editar à mão passa nos gates comuns e só o comparador acusa |
| registro central | `index.ts`, `mod.rs`, roteador, barrel, DI container | toda feature nova escreve na mesma linha |
| lockfile | `package-lock.json`, `Cargo.lock`, `poetry.lock` | merge de duas edições é sempre conflito |

Some a isso qualquer par de arquivos que a própria documentação do projeto marque como "não mexer em paralelo".

**7. O que é `human-only` neste projeto.** A lista genérica está na Fase 2; complete-a com o que este repositório exigir (uma conta, um runner específico, um direito administrativo, uma assinatura, uma segunda máquina).

Tudo isso vai para a seção **Perfil do projeto** do `TRIAGE.md` — é o que a `spec-loop` e todo subagent vão ler depois, e é o que evita que cada agente redescubra a mesma coisa.

---

## As três coisas que esta skill existe para impedir

**A documentação mente com autoridade.** Já se viu, em bases reais: um roadmap dizendo "não implementado" sobre algo entregue no mesmo dia; pendências mandando verificar código removido um milestone antes; e o arquivo de regras — justamente o que todo agente é mandado ler — descrevendo um estado meses atrasado. **Por isso a Fase 1 vem antes da Fase 2:** inventariar sobre documentação não reconciliada é inventariar trabalho que não existe.

**Número copiado para a prosa envelhece, e ninguém percebe.** Contagem de teste, número da próxima migração, tamanho de artefato, contagem de chaves. Um baseline de testes que ficou parado enquanto a suíte crescia é o pior caso, porque ele é usado como **gate**: a prosa errada vira critério de aprovação errado. Todo número que esta skill escreve num documento vem de uma medição feita nesta run (Fase 0, item 3).

**Resposta que fica só no relatório não existe.** O agente que vai implementar começa frio e lê a spec, não o histórico da conversa. Uma decisão do usuário registrada apenas no journal obriga a perguntar de novo na sessão seguinte — e acabar com isso é o propósito desta skill. Ver o contrato da Fase 3.

---

## Fase 1 — Reconciliar antes de inventariar

Objetivo: fazer a documentação descrever o projeto que existe hoje.

**Despache um subagent de auditoria** — somente leitura. O brief está em [references/auditor-brief.md](references/auditor-brief.md); passe a ele o **Perfil do projeto** da Fase 0, porque ele começa frio.

Cubra os quatro papéis de documento que a Fase 0 identificou. ⚠️ **O retrato do código é o mais esquecido e o mais perigoso.** Numa auditoria real, varrer só estado/roadmap/tasks achou 5 divergências; incluir os documentos de arquitetura e convenções achou 24 — entre elas um guia de convenções cujos exemplos apontavam todos para uma feature removida um milestone antes, e um documento de arquitetura afirmando que não havia versionamento de banco, sobre um banco com oito migrações versionadas. É o pior lugar para haver mentira: são os arquivos que dizem ao agente **como escrever código**, então quem obedecer copia exemplo que não compila.

Você então aplica as correções — você mesmo, porque é bookkeeping e é o produto do seu próprio raciocínio.

**Regras de correção:**

- Requisito ou pendência que perdeu o objeto é **riscado com o motivo**, nunca apagado. Nomeie o que o revogou (a spec, a decisão, o commit). O histórico do "por quê" tem valor.
- Marque como **"sem objeto, não verificado"**, nunca como "feito". Não foi verificado; deixou de haver o que verificar. É a mesma distinção entre "compila" e "funciona".
- Se o escopo de um milestone mudou, o roadmap e o topo do documento de estado mudam **juntos**.
- Número reescrito vem da medição da Fase 0, e o comando que o mediu vai para o `TRIAGE.md`.

**Saída:** a tabela de divergências, com o que foi corrigido e o que ficou pendente.

---

## Fase 2 — Inventário e classificação

### Como ler o estado de uma task (raramente há fonte única)

Conjuntos de spec crescem com convenções inconsistentes por herança. Consulte nesta ordem e pare no primeiro que responder:

1. **O header da task** no arquivo de tasks da feature — ou o campo de status no rastreador externo, conforme o item 2 do perfil — e qualquer marca nele (`[P]` para paralelizável, glifos de status).
2. **A tabela de log de execução**, se houver — normalmente uma linha por task com evidência.
3. **A prosa de status** no topo do arquivo — costuma dizer o que a tabela não diz ("sobram dois itens da T9 que exigem clique").
4. **O documento de estado do projeto** — é onde moram as pendências que atravessam features.

⚠️ **Checkbox dentro de uma task concluída é critério de aceitação, não pendência.** Um grep ingênuo por `- [ ]` numa base real devolveu ~337 itens quando o número de tasks realmente abertas era próximo de zero. Só conte os checkboxes de uma task **não** concluída.

⚠️ **Nada disso é confiável sozinho.** Um status só vira verdade depois de conferido contra o código — é o que a Fase 1 produziu.

### Classificação

Cada item aberto recebe exatamente um rótulo:

| Rótulo | O que é | Destino |
| --- | --- | --- |
| `code` | implementável e provável por teste, e a spec já diz tudo que o implementador precisa | **spec-loop** |
| `uat-agent` | exige o produto rodando, mas um agente consegue dirigir | **spec-loop**, nunca em paralelo |
| `needs-decision` | implementável, mas falta uma escolha que só o usuário faz | **Fase 3** — vira `code`/`uat-agent` depois de respondida |
| `human-only` | exige máquina, conta ou permissão que nenhum agente tem | ninguém — só relate |
| `moot` | o código que ele descrevia não existe mais | a Fase 1 já deveria ter riscado |
| `blocked` | sem solução conhecida, com medição que descarta a óbvia | só relate, com o número |

**`human-only` é qualquer coisa que exija**: credencial ou conta que o agente não tem; direito administrativo na máquina; hardware físico, uma segunda máquina ou uma condição de rede; publicar para fora (release, deploy, registro de pacotes); assinatura ou aprovação de uma pessoa; um recurso pago. Complete com o que a Fase 0 achou.

**Cada item do inventário carrega, além do rótulo:** o **escopo** que ele toca (qual pacote/gate se aplica) e se a task **declara os arquivos** que vai mexer. Os dois são insumo direto da `spec-loop`: o escopo vai para o brief do implementador, e a ausência de arquivos declarados obriga a serializar aquele item. Item sem essas duas informações força a `spec-loop` a adivinhar, e ela vai adivinhar conservador — tudo em série, com o gate da raiz.

**A classificação é o produto desta skill.** É o que a `spec-loop` lê para saber o que executar sem parar. Um item marcado `code` que na verdade escondia uma decisão de produto vira uma onda estacionada lá na frente — errar aqui é caro.

**Se o inventário der zero itens abertos: pare e relate.** Não invente refatoração, não "melhore" o que ninguém pediu, não converta `blocked` em tentativa. "Não há o que executar, e eis por quê" é um resultado correto.

---

## Fase 3 — Portão de decisões

Aqui todo `needs-decision` é resolvido, e o resultado é **gravado na spec** — não no relatório.

### 1. Levantar todas de uma vez

Varra o inventário e junte **tudo** que exige o usuário:

- perguntas em aberto ("Open Questions") nos documentos de desenho das features envolvidas;
- itens `blocked` onde existe mais de um caminho e a escolha é de produto, não técnica;
- tasks cuja spec admite **duas leituras** que levariam a trabalhos diferentes;
- qualquer coisa que **contradiga uma decisão já registrada** — cite a decisão na pergunta;
- mudança que implica **remover algo que hoje funciona**, sem estar dito se a remoção é intencional;
- mais de um lugar razoável para a mudança morar (camada A vs. camada B, store vs. componente);
- tudo que a `spec-loop` estacionou numa run anterior — procure por `⛔ NEEDS-DECISION` no conjunto de specs inteiro (com rastreador externo, procure também os tickets com esse rótulo).

**Não pergunte o que o repositório responde.** Leia as specs e o código primeiro. Pergunta boa é a que só o usuário pode responder — e a resposta costuma estar numa decisão já registrada que ninguém releu.

### 2. Escrever a lista no `TRIAGE.md` **antes** de perguntar

A lista inteira vai para o disco antes da primeira pergunta. Uma triagem interrompida no meio do interrogatório precisa que o arquivo já saiba o que faltava — senão a sessão seguinte refaz o levantamento e faz o usuário responder de novo o que ele já respondeu.

### 3. Perguntar uma de cada vez

Uma pergunta por vez, com as opções reais e o **trade-off de cada uma**. Quando houver número que sustente a escolha (uma medição, um tamanho, uma contagem), traga o número na pergunta: escolher entre quatro opções com a medição ao lado é uma decisão; escolher entre quatro adjetivos é um chute do usuário.

### 4. O contrato: gravar a resposta onde o implementador vai ler

**Este é o entregável da skill.** Uma resposta registrada só no `TRIAGE.md` não torna a spec executável — o subagent implementador começa frio, lê a spec, e não viu esta conversa.

Assim que cada resposta chega, grave nos lugares que se aplicarem:

| Onde | O que vai | Obrigatório? |
| --- | --- | --- |
| o arquivo de contexto da feature (`context.md` ou equivalente) | a decisão do usuário, com a data | sim |
| o requisito ou o desenho da feature | o texto **reescrito** para não admitir mais a segunda leitura; a pergunta aberta fechada com a resposta | sim, quando a dúvida era sobre requisito ou desenho |
| o registro de decisões do projeto | uma decisão nova, com o trade-off e o motivo | quando a escolha não é óbvia |
| o ticket no rastreador externo | a mesma resposta, com link para o arquivo do repositório | quando o perfil diz que há rastreador |
| `TRIAGE.md` | a resposta + **onde ela ficou gravada** | sim |

**Com rastreador externo, a ordem importa:** grave primeiro no repositório, depois espelhe no ticket. O ticket é conveniência para humano; o arquivo é o que o implementador lê. Se você só comentar no ticket, o próximo agente vai implementar sem a decisão e ninguém vai perceber até a validação.

Depois de gravar, aplique o teste que decide se o item está pronto:

> **Um agente que leia só a spec da feature, sem esta conversa, consegue implementar isto sem perguntar nada?**

Se a resposta for não, a spec ainda não foi atualizada o suficiente — volte e escreva. Só quando for sim o item muda de `needs-decision` para `code`/`uat-agent`.

Se a resposta do usuário criou um requisito que não existia, **crie o requisito na spec primeiro**, com o ID no padrão da feature e a rastreabilidade atualizada junto. Não invente ID fora do padrão que a Fase 0 descobriu.

### 5. Fechar a triagem

Só com a lista esgotada. Se sobrar pergunta sem resposta, a triagem fecha com `Status: bloqueada` e os itens correspondentes seguem `needs-decision` — a `spec-loop` vai ignorá-los, que é o comportamento certo.

---

## Fase 4 — O arquivo de triagem

Local: uma pasta de run dentro do conjunto de specs — `<specs>/runs/<NNN>-<YYYY-MM-DD>/TRIAGE.md`. A `spec-loop` escreve o `JOURNAL.md` na **mesma pasta**: uma run é uma triagem seguida de zero ou mais execuções.

⚠️ **O template abaixo está em português porque esta skill está.** Os artefatos seguem o **idioma de documentação descoberto na Fase 0**, não o idioma desta skill: num repositório em inglês, os títulos de seção, os rótulos de status e a prosa saem em inglês. O que não muda são os nomes de arquivo (`TRIAGE.md`, `JOURNAL.md`) e os rótulos de classificação (`code`, `uat-agent`, `needs-decision`, `human-only`, `blocked`, `moot`) — eles são o contrato entre as duas skills, e traduzir isso quebra a `spec-loop`.

```markdown
# Triagem NNN — <data>

**Status:** em andamento | pronta | bloqueada
**Revisão ao fechar:** <saída do comando de revisão do perfil, ou "SEM VCS — frescor não verificável">
**Perguntas em aberto:** <n>   ← se > 0, o Status NÃO pode ser "pronta"

## Perfil do projeto (Fase 0)
- Conjunto de specs: <caminho> — estado: <arquivo> | roadmap: <arquivo> | codebase: <caminho>
- Tasks moram em: <markdown no repo | rastreador externo <qual> | híbrido>
  - decisão do usuário é gravada em: <arquivo do repositório> (fonte)
  - espelhada em: <ticket/board> (conveniência)
  - tasks declaram os arquivos que tocam: <sim | não → spec-loop serializa>
- Controle de versão: <git|hg|svn|nenhum> — revisão: `<comando>` | estado: `<comando>`
- Regras do repositório: <arquivos lidos> — marcador de rastreabilidade: <formato ou "não exigido">
- Idioma: código <x> / documentação <y>
- Gates por escopo (comando → medição desta run):
  | escopo | comando | resultado medido |
- Território compartilhado: <lista, com o motivo de cada um>
- `human-only` neste projeto: <lista>

## Divergências encontradas (Fase 1)
| Afirmação | Onde | O que o código diz | Evidência | Gravidade | Corrigido? |

## Inventário (Fase 2)
| Item | Feature | Escopo/gate | Declara arquivos | Classificação | Pronto p/ execução | Por quê (se não) |

## Decisões do usuário (Fase 3)
Escrito ANTES da primeira pergunta.

| # | Pergunta | Por que só o usuário responde | Resposta | Data | Onde ficou gravada |

## Fora da execução
| Item | Rótulo | Por quê |

## Não verificado
<o que ficou sem prova — obrigatório, mesmo que vazio explique>
```

**Retomar uma triagem:** ler o `TRIAGE.md` mais recente com `Status: em andamento` ou `bloqueada` e seguir da primeira pergunta sem resposta. Nunca repita pergunta já respondida.

**Sem commits**, a menos que o usuário peça. Ao fim, **sugira** a mensagem; não execute.

---

## Nunca faça

- **Não implemente.** Nenhuma edição em código sai desta skill. Achou um bug durante a auditoria? Ele vira item do inventário, não um patch.
- **Não adivinhe a resposta do usuário** para "adiantar" a triagem. Um `needs-decision` chutado é pior que um pendente: entra na execução com autoridade e ninguém depois sabe que foi chute.
- **Não escreva número que você não mediu nesta run.**
- **Não toque em dados reais do usuário.** Se o projeto tem estado local (banco, cache, workspace), trabalhe sobre cópia em diretório temporário.
- **Não commite, não force-push, não reescreva branch principal** sem o usuário pedir.
- **Não invente ID de requisito.**

---

## Relatório final

Relate o que foi **executado**, não o que deveria funcionar:

- **quantas divergências** foram achadas e corrigidas, quais ficaram pendentes — com evidência (comando + saída), nunca adjetivo;
- **o inventário por rótulo**, com o número de itens em cada;
- **quantas perguntas** foram feitas e respondidas, e **onde cada resposta foi gravada** — este é o entregável, então nomeie os arquivos;
- **quantos itens estão prontos para a `spec-loop`**, quantos continuam fora e por quê;
- **o que NÃO foi verificado** — obrigatório, na mesma frase que descreve o que foi feito;
- **o que depende do usuário**, nomeando por que nenhum agente resolve.

Se sobrou item `code`/`uat-agent`, termine dizendo que a `spec-loop` pode rodar, e em qual pasta está o `TRIAGE.md`.
