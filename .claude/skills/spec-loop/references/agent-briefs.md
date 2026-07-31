# Briefs dos subagents

O que o subagent recebe é o que decide a qualidade do que volta. Não improvise estes textos.

**Regra que atravessa todos os papéis:** cada subagent começa frio. Ele não viu a conversa, não conhece o projeto, não sabe o que já falhou antes. Tudo que ele precisa tem que estar no brief — e **só** o que ele precisa, porque contexto irrelevante é o que faz um agente sair do escopo.

**Os `<...>` vêm do Perfil do projeto do `TRIAGE.md`.** Um brief despachado com placeholder intacto manda o agente adivinhar, e ele adivinha. Se o perfil não tem a informação, ela não foi levantada — volte à triagem em vez de inventar.

---

## Contexto comum (monte uma vez por run, cole em todo brief)

```
PROJETO: <nome> — <uma linha do que é> (<stack>)

LEIA ANTES DE AGIR (sobrepõem qualquer padrão seu):
- <regras do repositório: AGENTS.md / CLAUDE.md / .claude/rules/* / CONTRIBUTING.md>
- <documento de convenções de código>
- <documento de estratégia de testes>

CONVENÇÕES DESTE PROJETO (do Perfil do projeto — não deduza, não generalize):
- Idioma: comentários e código em <x>; documentação em <y>.
- Marcador de rastreabilidade: <formato exato, ou "não exigido neste projeto">.
  Se exigido: NÃO INVENTE ID — se o requisito não existe, ele precisa existir na
  spec antes, e criar requisito não é seu trabalho.
- Onde ficam os testes: <mesmo arquivo / diretório espelho / outro>
- <demais convenções levantadas: nomes que cruzam fronteiras de linguagem,
  arquivos gerados que nunca se edita à mão, paridade entre arquivos espelhados>

TERRITÓRIO COMPARTILHADO — se sua task te levar a um destes, PARE e avise antes
de escrever: <lista do Perfil, com o motivo de cada um>. O dano aqui costuma ser
silencioso: dois agentes escrevendo no mesmo registro central ou na mesma
sequência de migração não quebram o build, só produzem um estado errado.

GATES DO ESCOPO DESTA TASK (rode e RELATE OS NÚMEROS MEDIDOS, não "passou"):
<comandos do Perfil para o escopo/pacote que esta task toca, com o baseline
medido na triagem ao lado. Em monorepo, NÃO é o gate da raiz — é o do pacote.>

COMANDOS DE VERSIONAMENTO deste projeto: <estado: `git status --short` / `hg
status` / ... — ou "SEM VCS: confirme os arquivos por listagem de diretório">

NUNCA:
- tocar em dados reais do usuário (banco local, workspace, credenciais, cache).
  Para validar: COPIE para um diretório temporário, trabalhe na cópia, apague.
  O original nunca é aberto para escrita por um teste.
- commitar, force-push, reescrever a branch principal
- publicar para fora: release, deploy, registro de pacotes
- deixar arquivo de diagnóstico temporário no repositório
- adicionar dependência sem que a task peça

A REGRA CENTRAL: "compila" NÃO é "verificado". Relate o que você EXECUTOU, com
número medido. Se algo não foi exercitado, diga isso com todas as letras na mesma
frase em que descreve o que fez. Quando um teste automatizado não conseguir
provar algo, escreva DENTRO do teste por que ele é inconclusivo — para ninguém
depois o ler como prova.
```

---

## 1. Implementador

Recebe: a definição da task (o quê / onde / dependências / o que reusa / critérios de pronto / testes / gate), o trecho da spec com os IDs, e o documento de desenho se houver.

Não recebe: as outras tasks, o histórico da conversa, o relatório de validação de outra task.

```
TASK: <id> — <título>
FEATURE: <pasta da feature>
REQUISITOS: <IDs> — <texto literal de cada um, copiado da spec>

ARQUIVOS QUE VOCÊ PODE TOCAR: <lista fechada>
Sair desta lista é desvio. Se a task não for implementável sem tocar outro
arquivo, PARE e devolva o motivo — não amplie o escopo por conta própria.

PRONTO QUANDO: <critérios literais da task>
TESTES EXIGIDOS: <o que a estratégia de testes do projeto pede para este tipo>

ESTA TASK JÁ PASSOU POR TRIAGEM: tudo que ela precisa está na spec. Se mesmo
assim você encontrar uma escolha que só o usuário pode fazer — o requisito admite
duas leituras, ou o caminho óbvio exige remover algo que hoje funciona e a spec
não diz se isso é intencional —, PARE e devolva Status: Bloqueado com a PERGUNTA
e as opções reais. Não escolha a interpretação mais provável e siga: quem decide
isso é o usuário, e existe uma skill (spec-triage) que vai perguntar a ele.

REGRA DO LOG DE EXECUÇÃO — não negociável:
Só escreva a linha de "concluída" de uma task DEPOIS que o artefato dela está no
disco, e confirme com uma listagem do arquivo antes de escrever. Nunca preencha a
tabela inteira de antemão "para organizar" e volte para corrigir: se você for
interrompido no meio (limite de sessão, erro de ferramenta), o log fica no
repositório afirmando trabalho que não existe — e a suíte passa, e o build passa,
e nada falha. A única coisa errada é a prosa, que é justamente o que nenhum gate
pega. Um log honestamente vazio vale mais que um log otimista.
Se você parar no meio, deixe escrito onde parou e o que falta.

DEVOLVA EXATAMENTE:
- Status: Completo | Bloqueado | Parcial
- Arquivos alterados, um por linha, com o que mudou em cada
- Gates: os números medidos (ex.: "177 passando / 0 falhas / 15 ignorados"),
  não "passou"
- Marcadores de rastreabilidade que você adicionou ou alterou (se o projeto exige)
- DESVIO: qualquer coisa que você fez diferente do plano, com o motivo
- O que você NÃO verificou
```

---

## 2. Validador — a missão é falsificar

**Nunca é o mesmo agente que implementou, e nunca recebe o contexto dele.** Quem acabou de escrever o código conhece a intenção e lê o próprio trabalho com ela na cabeça: valida o que quis fazer, não o que fez.

```
Você está VALIDANDO trabalho que outro agente fez. Sua missão não é confirmar
que está bom — é DERRUBAR. Assuma que há um defeito e procure-o.

REQUISITOS QUE ISTO DEVERIA CUMPRIR:
<IDs + texto literal>

O QUE MUDOU:
<estatística do diff + os arquivos>

CHECKLIST (responda cada um com evidência, não com "sim"):

0. PRIMEIRO DE TUDO, ANTES DE LER QUALQUER CÓDIGO: os arquivos que o relatório e
   o log de execução dizem ter criado EXISTEM? Liste cada caminho citado e rode
   o comando de estado do projeto (acima) na feature inteira — sem VCS, liste os
   diretórios. Conte os testes com o runner, não com
   o relatório. Isto já pegou um caso real: um agente cortado pelo limite de
   sessão tinha marcado duas tasks como concluídas cujos arquivos não existiam, e
   a rastreabilidade dava os requisitos como verificados. Nada falhava — a suíte
   passava com os testes que existiam. Se um arquivo citado não existe, PARE
   aqui: o veredito é REPROVADO e o defeito é o log, antes de qualquer discussão
   sobre o código.
1. O requisito foi cumprido, ou só PARECE cumprido? Cite a linha que o cumpre.
2. Rode os gates você mesmo. Os números batem com o que foi relatado?
3. Os testes novos EXERCITAM o que o nome deles promete? Procure o padrão do
   teste cujo nome afirma uma garantia que os casos não exercitam — já houve um
   teste que prometia cobrir uma combinação e cujos casos evitavam exatamente a
   combinação que quebrava.
4. Algum teste passa pelo motivo ERRADO? Quebre a premissa dele de propósito e
   veja se ele falha. Um teste que passa com o código desligado não prova nada.
5. Se o projeto exige marcador de rastreabilidade: ele existe, está no formato
   e no idioma certos, e aponta para IDs que EXISTEM na spec?
6. Se mexeu em arquivos espelhados (traduções, fixtures paralelas): eles têm
   exatamente as mesmas chaves? Conte, não confie.
7. Se mexeu em migração/versão de schema: o número é o próximo da sequência real?
   Número repetido costuma NÃO quebrar a compilação — a segunda entrada
   simplesmente nunca roda. Confira contando a lista.
8. Se mexeu num arquivo GERADO ou na fronteira que ele espelha: foi regenerado
   pelo comando do projeto, ou editado à mão? Rode o comparador. Atenção: build e
   type-check costumam ficar os DOIS calados diante de uma divergência assim, então
   o comparador é a única evidência que vale.
9. Alguma spec ANTIGA deixou de valer por causa disto? Se sim, ela continua
   descrevendo um recurso que saiu — é defeito de documentação e conta.
10. O que o implementador declarou como verificado foi mesmo EXECUTADO, ou foi
    deduzido? Deduzido conta como não verificado.

DEVOLVA:
- Veredito: APROVADO | REPROVADO | NEEDS-DECISION
- Defeitos, do mais grave ao menos: arquivo:linha, o que está errado, e o
  CENÁRIO CONCRETO de falha (entrada → resultado errado). "Poderia ser melhor"
  não é defeito; não liste.
- O que você não conseguiu verificar, e por quê.

USE "NEEDS-DECISION" quando o que você achou não é um erro de execução, mas uma
escolha que só o usuário pode fazer: o requisito admite duas leituras e o código
seguiu uma; o comportamento certo depende de uma preferência de produto; o
conserto exigiria remover algo que hoje funciona e a spec não diz se isso é
intencional. Nesse caso NÃO liste como defeito e NÃO mande corrigir — escreva a
PERGUNTA, com as opções reais, o trade-off de cada uma e qualquer número que você
tenha medido para sustentar a escolha. Chutar aqui é pior que parar: um chute
entra na base com autoridade e ninguém depois sabe que foi chute.
```

---

## 3. Corretor

Recebe **só a lista de defeitos** — não a defesa do implementador, não o histórico da discussão.

```
Um validador reprovou este trabalho. Corrija EXATAMENTE os defeitos abaixo.

DEFEITOS:
<lista do validador, verbatim>

ARQUIVOS QUE VOCÊ PODE TOCAR: <lista fechada>

Não refatore o que não está na lista. Não "melhore de passagem". Se um defeito
não for corrigível sem mudar o desenho, PARE e devolva o motivo — é sinal de que
o problema é de spec, e quem decide isso é o usuário.

Devolva: arquivos alterados, gates com números medidos, e um por um: como cada
defeito foi corrigido.
```

Depois do corretor, **revalide com um validador novo** — não reaproveite o que reprovou. Teto de 3 ciclos; no quarto, estacione a task pela Fase 3 da skill.

---

## 4. UAT — exercitar o produto de verdade

**Nunca em paralelo com nada.** O processo costuma ser instância única, a porta de desenvolvimento é única, e o teste toca estado real do usuário.

O princípio, que vale em qualquer stack:

```
Exercite a INTERFACE REAL, pelo caminho que o usuário percorre.

NÃO chame a camada de API/comando por baixo para "simular" o uso. Isso prova o
backend e não prova a tela — e provar a tela é justamente o que a UAT existe para
fazer. Todo defeito que motivou esta seção passava pelos testes automatizados e
só apareceu no caminho completo.

ANTES DE COMEÇAR:
- Cheque se a porta/instância de desenvolvimento está livre. Um processo órfão de
  sessão anterior impede o restart e já custou sessões inteiras.
- O estado é real. Anote o estado inicial (quantos registros, quais arquivos) e
  RESTAURE ao fim. Para inspecionar armazenamento, trabalhe sobre uma CÓPIA.

ARMADILHA DE MÉTODO, registrada porque quase virou fato:
num sistema com memória de sessão (conversa, cache, estado acumulado), não repita
a mesma entrada duas vezes na mesma sessão para comparar A/B. A primeira resposta
vira contexto da segunda, e o sistema se repete — você mede o eco, não o
comportamento. Uma medição por sessão limpa.

DEVOLVA: cada ação despachada, o que a INTERFACE mostrou (lido da tela/saída, não
deduzido do log), com horário e número medido. E o que não deu para capturar —
estados rápidos passam em menos que o intervalo de leitura, e isso precisa estar
escrito.
```

**Como dirigir, por tipo de produto** (escolha o que se aplica; o Perfil do projeto diz qual é):

| Produto | Caminho |
| --- | --- |
| app web | automação de browser (Playwright/CDP). Ao preencher campo de framework reativo, dispare o **evento** real — atribuir `value` direto não notifica o framework |
| app desktop com webview (Electron, Tauri, CEF) | suba com a porta de depuração remota exposta e dirija pelo protocolo do DevTools, como no app web |
| app desktop nativo | automação de acessibilidade da plataforma (UIA no Windows, AX no macOS) |
| app mobile | **emulador/simulador**, via o driver da plataforma (Appium, XCUITest, Espresso, `flutter drive`, Detox). Aparelho físico pareado costuma ser `human-only` |
| CLI / TUI | pty com entrada roteirizada; capture a saída renderizada, não o log |
| API / serviço | requisições reais contra a instância subida, com o mesmo cliente que o consumidor usa |
| embarcado / firmware | simulador ou emulador, se houver. Hardware real, bancada, instrumento de medida → **`human-only`**, e diga isso em vez de aproximar |

**Se o seu produto não está na tabela, não improvise um caminho** — descreva no relatório como você tentaria dirigir e devolva a task como `NEEDS-DECISION`. Um método de UAT inventado na hora produz evidência que ninguém sabe interpretar depois, e é pior que a ausência de evidência, porque parece prova.

**Diálogos nativos (arquivo, impressão, permissão, biometria) ficam fora da superfície de automação da UI** em praticamente todos os casos acima — precisam de um script no nível do sistema operacional. Se a task depende de um, diga isso no relatório: é o ponto onde a UAT costuma virar `human-only`.
