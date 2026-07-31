---
name: spec-loop
description: Executa o que a triagem já marcou como pronto em qualquer projeto — despacha subagents em paralelo, cada execução seguida de uma validação adversarial por um agente diferente, com correção em loop. Nunca pergunta ao usuário: item que exige decisão humana é estacionado, marcado na spec e devolvido para a skill spec-triage. Mantém um journal que permite retomar numa sessão nova. Use quando o pedido for "execute o que falta", "continue de onde parou", "valide o que foi implementado" ou variações.
---

# spec-loop — execução e validação orquestradas

Esta skill é **orquestradora e não-bloqueante**. Ela executa; ela não decide o que é o trabalho e não interroga o usuário.

| Skill | Faz | Não faz |
| --- | --- | --- |
| **spec-triage** | descobre o projeto, reconcilia a documentação com o código, inventaria, classifica, pergunta ao usuário e grava a resposta na spec | não implementa |
| **spec-loop** (esta) | executa os itens que a triagem marcou como prontos, com validação adversarial em loop | **não reconcilia, não classifica, não pergunta** |

**A regra que define esta skill:** ela só toca item que já é executável sem intervenção humana. Se durante a execução ou a validação aparecer uma decisão que só o usuário pode tomar, o item é **estacionado e a spec dele é atualizada** com a pergunta — nunca executado no chute, nunca perguntado no meio da onda. A Fase 3 diz como.

Quem executa esta skill **não edita código, não roda gate, não dirige o produto**: planeja ondas, despacha subagents, lê o que eles devolvem e decide o próximo passo. Toda mudança de arquivo passa por um subagent.

A razão não é estética. O contexto do orquestrador precisa durar a run inteira — se ele gastar o contexto lendo diffs e saída de teste, ele perde a única coisa que só ele tem: a visão de quais tasks colidem, o que já foi validado e o que ficou pendente. Um agente que implementa perde essa visão em três tasks.

**As exceções, e elas têm fronteira exata.** O orquestrador escreve:
- a documentação de **nível projeto** (estado, roadmap, retrato do código, regras do repositório) e o journal — é bookkeeping, é o produto do próprio raciocínio dele, e delegar isso significaria delegar a memória da run;
- a **nota de estacionamento** de um item devolvido à triagem (Fase 3) — também é bookkeeping: registra o que a run encontrou, não planeja a feature.

A documentação de **nível feature** (requisitos, desenho, tasks) é escrita pelo **agente que planeja aquela feature**. Ela é o produto do planejamento, não bookkeeping — e centralizá-la faria o orquestrador virar gargalo de digitação enquanto dois agentes esperam.

**Esta skill não conhece o seu projeto.** Onde ficam as specs, quais são os gates, o que é território compartilhado, o que exige o usuário: tudo isso vem do `TRIAGE.md` que a `spec-triage` produziu. Nomes de arquivo citados aqui são exemplo, não fato.

---

## As três coisas que esta skill existe para impedir

**"Compila" não é "verificado".** Um agente que reporta "implementado, os testes passaram" não provou nada sobre o produto. Em bases reais, sessões de teste manual acharam defeitos que passavam por **todos** os gates automatizados: uma dependência podada do pacote final, um dado gravado que nunca era lido de volta, um resultado plausível construído sobre a entrada errada. Por isso a validação desta skill é adversarial, e por isso `uat-agent` existe como classe separada.

**Um relatório otimista não falha nenhum gate.** Já aconteceu de um agente cortado por limite de sessão marcar duas tasks como concluídas cujos arquivos não existiam, com a rastreabilidade dando os requisitos como verificados — e nada quebrar, porque a suíte passava com os testes que de fato existiam. A única coisa errada era a prosa, que é justamente o que nenhum gate pega. É o item 0 do checklist do validador.

**Executar sobre documentação não reconciliada é executar trabalho que não existe.** Esta skill **não faz** essa reconciliação: ela exige que já tenha sido feita, e verifica isso na Fase 0.

---

## Fase 0 — Carregar a triagem (pré-condição, não trabalho)

Esta skill não descobre o que fazer. Ela lê o que a `spec-triage` já decidiu.

1. Ache o `TRIAGE.md` mais recente em `<specs>/runs/<NNN>-<YYYY-MM-DD>/`.
2. **Ele precisa estar com `Status: pronta`.** `em andamento` ou `bloqueada` significa que ainda há pergunta aberta com o usuário.
3. **Ele precisa estar fresco.** Rode o **comando de revisão do perfil** (`git rev-parse --short HEAD`, `hg id -i`, `svnversion` — o que o projeto usar) e compare com a `Revisão ao fechar` registrada. Se avançou, o código mudou depois da triagem e a classificação pode ter envelhecido.

   **Se o perfil disser "SEM VCS — frescor não verificável", a regra é mais dura:** a triagem só vale na sessão em que foi feita. Numa sessão nova, você não tem como saber o que mudou no disco desde então — peça a triagem de novo. Aceitar calado um `TRIAGE.md` sem revisão é executar classificação velha achando que está fresca, e nada no caminho vai reclamar.

**Se qualquer uma das três falhar: pare e peça a triagem.** Não improvise um inventário, não "dá para ver rapidinho o que falta", não classifique por conta própria. Uma frase basta: *"não há triagem pronta (ou ela está velha) — rode a skill `spec-triage` primeiro."* Este é o modo de falha mais provável desta skill, porque o atalho parece produtivo.

**Se não existir `TRIAGE.md` nenhum**, o mesmo vale: a triagem é sempre a primeira execução do par.

Com a triagem carregada, leia dela o **Perfil do projeto** — é o que substitui todo conhecimento específico que esta skill deliberadamente não tem:

| Do perfil | Usado em |
| --- | --- |
| caminho do conjunto de specs e dos documentos de projeto | todas as fases |
| onde as tasks moram e onde a decisão fica gravada | nota de estacionamento (Fase 3) |
| controle de versão e seus comandos | frescor (acima), checkpoint e retomada (Fase 4) |
| regras do repositório (incluindo marcador de rastreabilidade e idioma) | brief de todo subagent |
| **gates por escopo** + o baseline medido na triagem | brief do implementador e do validador — cole o gate do **escopo daquela task**, não o da raiz |
| território compartilhado, e se a task declara seus arquivos | montagem das ondas (Fase 1) |

**O idioma dos artefatos é o do perfil, não o desta skill.** Journal, notas de estacionamento e relatório saem no idioma de documentação do projeto. Só os rótulos de classificação (`code`, `uat-agent`, `needs-decision`…), os nomes de arquivo e o marcador `⛔ NEEDS-DECISION` ficam como estão: são contrato com a `spec-triage`.

E monte a fila, que é exatamente esta e nada além dela:

| Rótulo no inventário | Entra na fila? |
| --- | --- |
| `code` com **Pronto p/ execução = sim** | sim |
| `uat-agent` com **Pronto p/ execução = sim** | sim, sempre sozinho |
| `needs-decision` | **não** — é da triagem |
| `human-only`, `blocked`, `moot` | **não** — só aparecem no relatório final |

**Se a fila der zero: pare e relate.** Não invente refatoração, não "melhore" o que ninguém pediu, não converta `blocked` em tentativa. "Não há o que executar, e eis por quê" é um resultado correto.

---

## Fase 1 — Ondas de paralelismo

Paralelizar é o objetivo, mas colisão custa mais do que a economia. Uma task entra na onda com outra **só se todas as condições valerem**:

1. **Conjuntos de arquivos disjuntos.** Leia o campo de arquivos da task. Interseção não vazia → ondas diferentes.

   **Task com `Declara arquivos = não` no inventário vai sozinha.** Sem essa lista você não tem como provar disjunção, e supor que duas tasks não se cruzam é exatamente o erro que a onda existe para evitar. Serialize — e **escreva no journal que serializou por falta de arquivos declarados**, senão a run parece lenta sem motivo e ninguém conserta a causa, que é a spec.
2. **Sem dependência declarada ainda aberta.**
3. **Nenhuma é `uat-agent`.** Dirigir o produto é sempre sozinho: o processo costuma ser instância única, a porta de desenvolvimento é única, e o teste manual toca estado real.
4. **Nenhuma toca o território compartilhado listado no `TRIAGE.md`** — o padrão típico é migração numerada, arquivos de tradução espelhados, arquivo gerado, registro central, lockfile. O motivo de cada um está no perfil; se dois agentes escreverem lá, o dano costuma ser **silencioso**, não um build quebrado.

**Teto de 3 subagents de execução simultâneos.** Não é limite técnico: acima disso o orquestrador não consegue validar com cuidado o que volta, e validação superficial é o modo de falha que esta skill existe para evitar.

Despache as tasks de uma onda em **uma única mensagem** com múltiplas chamadas do Agent — é o que as faz rodar de fato em paralelo.

---

## Fase 2 — O loop de execução e validação

Para cada task da onda:

```
        ┌──────────────┐
        │ IMPLEMENTADOR│  subagent novo, contexto mínimo
        └──────┬───────┘
               ↓ devolve: arquivos, gates, desvios
        ┌──────────────┐
        │  VALIDADOR   │  subagent DIFERENTE, missão adversarial
        └──────┬───────┘
         aprovado? ──sim──→ journal + próxima
               │ não
               ↓
        ┌──────────────┐
        │  CORRETOR    │  recebe só a lista de defeitos
        └──────┬───────┘
               ↓
          revalidar (validador novo)  ── até 3 ciclos ──→ estaciona (Fase 3)
```

**O validador nunca é o implementador, e nunca recebe o contexto dele.** Um agente que acabou de escrever o código conhece a intenção e lê o próprio trabalho com ela na cabeça; ele valida o que quis fazer, não o que fez. O validador recebe o requisito e o diff, e a missão de **falsificar**.

**Teto de 3 ciclos por task.** Se um defeito sobrevive a três correções, o problema é de spec ou de desenho, não de código — e isso é decisão do usuário. Estacione pela Fase 3.

Os briefs de cada papel estão em [references/agent-briefs.md](references/agent-briefs.md). Não improvise, e **preencha os placeholders com o Perfil do projeto**: o que o subagent recebe é o que decide a qualidade do que volta.

---

## Fase 3 — Quando aparece uma decisão humana: estacionar, não perguntar

Acontece: um validador devolve `NEEDS-DECISION` em vez de defeito; um implementador para dizendo que a task admite duas leituras; três ciclos de correção provam que o problema é de desenho. Defeitos que só aparecem com o produto rodando são o caso mais comum.

Esta skill **não pergunta** — perguntar bloquearia a onda inteira por causa de uma task, e a pergunta feita no meio da execução é justamente a que custa retrabalho do código já escrito. O procedimento:

1. **Pare aquela task.** As outras da onda seguem até o fim. Uma task parada é barata; uma onda parada por uma pergunta de uma task, não.
2. **Reverta ou isole o que ficou pela metade.** Não deixe no working tree meio-código que ninguém validou. Se o trabalho parcial tem valor, ele fica — mas a nota diz exatamente o que está incompleto.
3. **Atualize a spec da task** — é a parte que não pode ser pulada. Este conteúdo, no idioma de documentação do projeto:

   ```markdown
   ### T7: <título>  ⛔ NEEDS-DECISION

   **Estacionada na run <NNN> (<data>).** Não executar até haver decisão do usuário.

   **Pergunta:** <a pergunta, com as opções reais e o trade-off de cada uma>
   **Por que só o usuário responde:** <o que no repositório não responde isto>
   **Medições que sustentam a escolha:** <número medido, com o comando>
   **Estado do código:** <o que ficou no disco, ou "nada — revertido">
   ```

   **Onde isso vai depende do perfil:**

   | Tasks moram em | Onde escrever |
   | --- | --- |
   | markdown no repositório | no header da task, no arquivo de tasks da feature |
   | rastreador externo | **no arquivo do repositório que o perfil aponta como fonte** (o `context.md` da feature ou equivalente), e só então espelhe no ticket com o rótulo `⛔ NEEDS-DECISION` |

   Nunca só no ticket. O subagent que pegar essa task na próxima run costuma não ter credencial do rastreador — ele vai ler a spec, não achar o impedimento, e implementar no chute exatamente o que você estacionou para não chutar.

   Se a dúvida for de desenho e não da task, abra também a pergunta no documento de desenho da feature. O critério é o mesmo da triagem: o próximo agente lê a spec, não esta conversa.
4. **Registre no journal**, na seção "Devolvido para triagem".
5. **Siga a run** com o resto da fila.

No relatório final, diga quantos itens voltaram e que a `spec-triage` precisa rodar para desbloqueá-los.

---

## Fase 4 — Journal, e retomar numa sessão nova

O journal é o que torna a run interrompível. **Escreva depois de cada task, não no fim** — uma run que morre no meio precisa que o disco já saiba o que aconteceu.

Local: `<specs>/runs/<NNN>-<YYYY-MM-DD>/JOURNAL.md` — a **mesma pasta** do `TRIAGE.md` que autorizou esta execução.

O template abaixo está em português porque esta skill está; **o journal sai no idioma de documentação do projeto**.

```markdown
# Run NNN — <data>

**Status:** em andamento | pausada | concluída
**Triagem que autorizou:** TRIAGE.md desta pasta, revisão <valor>
**Orquestrador:** sessão iniciada em <hora>

## Fila de execução (da triagem)
| Item | Feature | Escopo/gate | Classificação | Onda | (se sozinha) por quê |

## Execução
| Task | Onda | Implementador | Gates | Validação | Ciclos | Status |

## Devolvido para triagem
| Task | Pergunta | Onde ficou gravada | Estado do código |

## Gates medidos nesta run
| escopo | comando | resultado medido | quando |
(número medido nesta run — nunca copiado do TRIAGE.md nem de outro documento)

## Estado da árvore no último checkpoint
<saída do comando de estado do perfil — ou, sem VCS, a listagem de arquivos
tocados com mtime>

## Não verificado
<o que ficou sem prova de execução — obrigatório, mesmo que vazio explique>
```

**Retomar:** ler o journal mais recente com `Status: em andamento` ou `pausada`, rodar o comando de estado do perfil, comparar com o checkpoint registrado. Divergência significa que algo mudou fora da skill — reconcilie antes de continuar. Confira também que o `TRIAGE.md` da pasta continua valendo (Fase 0). Depois siga da primeira task sem `Status: concluída`.

**Sem VCS, a retomada é frágil e você precisa dizer isso:** sem diff, você não consegue distinguir o que esta run escreveu do que alguém escreveu entre as sessões. Retome mesmo assim, mas trate cada task já marcada como concluída como **não reverificada** e registre isso na seção "Não verificado".

**Sem commits**, a menos que o usuário peça — e a menos que as regras do repositório digam outra coisa. A retomada se apoia no journal + o estado da árvore, não no histórico. Ao fim da run, **sugira** a mensagem de commit; não execute.

---

## Nunca faça (vale para todo subagent despachado)

- **Não pergunte ao usuário no meio da execução.** Estacione pela Fase 3. A única pergunta legítima desta skill é a do fim: "posso commitar?".
- **Não execute item `needs-decision`, `human-only` ou `blocked`.** Se ele está fora da fila, ele está fora.
- **Não toque em dados reais do usuário.** Se o projeto tem estado local (banco, workspace, cache, credenciais), **copie** para um diretório temporário, trabalhe na cópia, apague. O original nunca é aberto para escrita por um teste.
- **Não commite, não force-push, não reescreva a branch principal** sem o usuário pedir. Desfazer é um commit de reversão, nunca reescrita de histórico.
- **Não publique nada para fora**: release, deploy, registro de pacotes. É `human-only` por definição.
- **Não deixe arquivo de diagnóstico temporário no repositório.** Órfãos com caminhos absolutos da máquina de alguém sobrevivem meses à investigação que os criou.
- **Não invente ID de requisito.** Criar requisito é trabalho da triagem, não desta skill.
- **As regras do repositório vencem** qualquer coisa escrita aqui. Se houver contradição, siga o repositório e registre a contradição no relatório.

---

## Relatório final

Relate o que foi **executado**, não o que deveria funcionar, e diga a origem de cada evidência:

- **o que rodou**, com número medido (contagem de teste, tempo, bytes) — nunca adjetivo;
- **quem provou o quê**: gate automatizado, validador adversarial, ou uso real do produto. As três têm forças diferentes e o leitor precisa saber qual foi;
- **quais specs foram atualizadas** e o que ficou pendente nelas;
- **quais marcadores de rastreabilidade** foram adicionados ou mexidos, se o projeto os exige;
- **o que voltou para a triagem**, com a pergunta de cada item;
- **o que NÃO foi verificado** — obrigatório, na mesma frase que descreve o que foi feito;
- **o que depende do usuário**, nomeando por que nenhum agente resolve.
