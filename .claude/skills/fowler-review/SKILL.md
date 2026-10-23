---
name: fowler-review
description: Valida uma implementação analisando só o que mudou — pergunta se o escopo são as alterações em stage ou os commits da branch atual comparados com a branch de origem (git diff) — e aponta erros e melhorias, valida nomes de funções, variáveis e constantes, números mágicos, duplicação de código e oportunidades de simplificação, e verifica se está bem organizada, segue o padrão do projeto e é fácil de entender e de mudar — usando o método de Martin Fowler (Refactoring, 2ª ed., caps. 1–3): teste de mudança, code smells e estrutura-alvo. Use quando o usuário pedir para validar, revisar ou avaliar uma implementação, diff, PR, arquivo ou função quanto a organização, padrão, nomes, legibilidade, duplicação, simplicidade, clareza, design, "código limpo", "boas práticas", "fácil de entender" ou code smells; ou quando citar Fowler. Só relata e recomenda — não altera código; grava a análise num arquivo .md na raiz do projeto.
---

# Fowler Review

Skill interna, derivada do livro *Refactoring: Improving the Design of Existing Code* (Martin Fowler, 2ª ed.), capítulos 1–3. Resumo próprio — não reproduz o texto do livro.

## Critério único

**Código bom é código fácil de mudar.** Quem precisar alterar deve achar rápido onde mexer e mudar sem introduzir erro. Gosto pessoal não é critério; todo achado tem que dizer *qual mudança futura* ele encarece ou *qual leitura* ele atrapalha.

Código feio que ninguém vai ler nem mudar não é problema — não reporte como grave.

## Procedimento

1. **Pergunte o escopo e monte o diff** (ver "Escopo da análise"). A revisão cobre **somente o que mudou** nesse diff.
   - Leia o código ao redor das linhas alteradas (função inteira, chamadores) o suficiente para entender o fluxo, mas **não reporte problemas em código que não foi alterado**.
   - Exceção: código existente entra no relatório só quando a mudança o duplica (V5) ou diverge do padrão dele (V7).
2. **Aprenda o padrão do projeto.** Abra 2–3 arquivos vizinhos do mesmo tipo e anote as convenções: estrutura de pastas/camadas, caixa e idioma dos nomes, verbos usados (`get`/`fetch`/`load`), onde ficam constantes, como trata erro. A revisão compara contra isso, não contra um padrão abstrato.
3. **Teste de mudança (lição do cap. 1).** Formule 2 mudanças plausíveis para esse código — ex.: novo formato de saída, novo tipo/variante, nova regra de cálculo, nova fonte de dados. Para cada uma: quantos lugares mudam? Haveria tentação de copiar e colar? Dá para mudar uma parte sem entender o resto? Esse é o diagnóstico principal.
4. **Rode as 7 verificações obrigatórias** (V1–V7 abaixo) sobre todas as linhas alteradas do diff.
5. **Leia pelas lentes de estrutura** (as transformações do exemplo do cap. 1):
   - **Organização** — cada coisa está no módulo/classe certo (dados junto do comportamento que os usa)?
   - **Decomposição** — função longa misturando vários "o quê"? Blocos com comentário explicando o que fazem?
   - **Estado** — temps que só guardam expressão derivável, acumuladores misturados num mesmo loop, dados mutáveis com escopo grande, dados globais.
   - **Fases** — cálculo misturado com formatação/IO/apresentação? Deveria haver uma fase que produz dados e outra que os consome (Split Phase).
   - **Condicionais por tipo** — `switch`/`if` sobre o mesmo tipo repetido em vários lugares → polimorfismo. Switch isolado normalmente é aceitável.
6. **Varra os code smells** com `references/smells.md` (24 cheiros). Reporte só o que encontrou de fato, com localização.
7. **Erros visíveis.** Bugs evidentes notados na leitura (caso não tratado, mutação inesperada, efeito colateral escondido, condição invertida, off-by-one) entram como 🔴 Crítica. Não é caça exaustiva a bugs — é o que a leitura cuidadosa revela.
8. **Prescreva cada melhoria pelo nome** do refactoring, consultando `references/catalog.md`.
9. **Estrutura-alvo.** Descreva em poucas linhas como o código ficaria bem organizado: funções/módulos/classes, qual fase faz o quê, onde mora cada responsabilidade (ver exemplo no fim de `references/catalog.md`).
10. **Testes.** Existem testes cobrindo o trecho? Ausência é achado.
11. **Grave o relatório** em Markdown na raiz do projeto (ver "Arquivo de saída").

## Escopo da análise

Antes de qualquer leitura, **pergunte ao usuário** onde a análise vai rodar (use a ferramenta de pergunta com opções, se disponível; senão, pergunte no chat e espere a resposta). Pule a pergunta só se o pedido já disser o escopo explicitamente.

**Opção A — Alterações em stage**
```bash
git diff --cached --name-only        # arquivos alterados
git diff --cached -U0                # linhas alteradas (hunks)
git diff --cached                    # diff com contexto, para leitura
```
Stage vazio → avise o usuário e pergunte se quer usar as alterações não staged (`git diff`) ou a opção B. Não analise nada sem confirmação.

**Opção B — Commits da branch atual vs. branch de origem**
1. Branch atual: `git branch --show-current`.
2. Sugira como base a branch padrão do remoto: `git symbolic-ref --short refs/remotes/origin/HEAD` (ex.: `origin/main`). Não use `@{upstream}`: numa feature branch ele aponta para a própria branch no remoto, não para a de origem. **Confirme a base com o usuário** — a branch pode ter saído de `develop`, de uma release etc.
3. Diff só do que a branch introduziu (três pontos = a partir do ponto em que a branch saiu da base):
```bash
git merge-base <base> HEAD           # ponto em que a branch saiu da base
git diff --name-only <base>...HEAD   # arquivos alterados
git diff -U0 <base>...HEAD           # linhas alteradas
git log --oneline <base>..HEAD       # commits analisados
```
Se a base local puder estar desatualizada, ofereça `git fetch origin <base>` antes (só com o "sim" do usuário).

**Regras para as duas opções:**
- Mudanças só de arquivos gerados, lockfiles, migrations geradas automaticamente, build/dist e binários ficam fora; liste-os como "ignorados".
- Arquivo removido não é analisado. Arquivo novo é analisado inteiro (tudo nele mudou).
- Diff muito grande (mais de ~40 arquivos ou ~2000 linhas) → avise e pergunte se analisa tudo ou só uma pasta ou módulo.
- Todo `path:linha` do relatório aponta para uma linha **adicionada ou alterada** no diff (exceto as referências de V5/V7 ao código existente).

## Verificações obrigatórias

### V1. Nomes de funções

Leia só nome e assinatura e diga o que a função faz; depois leia o corpo. Se divergem, o nome falhou.

1. **Intenção, não implementação** — diz *o que* resulta, não *como* (`totalVolumeCredits`, não `loopPerformancesAndSum`).
2. **Dispensa ler o corpo** — quem lê a chamada entende o efeito.
3. **Verdadeiro sobre efeitos colaterais** — nome de consulta (`get`, `calculate`, `is`, `find`, substantivo) não pode alterar estado, gravar ou enviar. Se altera: verbo de ação (`save`, `update`, `send`) ou dividir (Separate Query from Modifier). Efeito que surpreende = 🔴 Crítica.
4. **Uma coisa só** — "And"/"Or" no nome (`validateAndSave`) ou nome genérico (`process`, `handle`, `doStuff`, `manage`, `helper`, `util`) indica várias responsabilidades ou propósito indefinido.
5. **Booleano soa como pergunta** — `isEligible`, `hasItems`, `canEdit`; não `checkEligibility`.
6. **Sem flag que muda o sentido** — `render(data, true)` esconde o que `true` faz (Remove Flag Argument).
7. **Coerente com o contexto** — não repete o nome da classe (`order.getOrderTotal` → `order.total`); se "parece pertencer" a outro módulo, é Feature Envy.
8. **Consistente com o projeto** — mesmo verbo para a mesma operação em todo o código, mesma caixa e idioma.
9. **Termos do domínio** — `activeCustomers`, não `filterListByFlag`.
10. **Sem abreviação obscura nem nome enganoso** — nome que promete mais ou menos do que a função faz.

Sem nome bom possível → sinal de responsabilidade confusa; sugira dividir (Extract Function) antes de renomear. Correção: Change Function Declaration (em API publicada: nova função + antiga delegando, depreciada).

### V2. Nomes de variáveis, parâmetros e campos

1. **Revela o papel**, não o tipo nem a estrutura (`unpaidInvoices`, não `list2`/`arr`/`data`/`obj`/`tmp`/`res`).
2. **Escopo define o tamanho** — nome de uma letra só em escopo de 1–3 linhas (índice de loop, lambda curta); quanto maior o escopo e mais usado, mais descritivo.
3. **Unidade explícita** quando há unidade (`timeoutMs`, `priceInCents`, `distanceKm`) — ou tipo próprio (Replace Primitive with Object).
4. **Booleanos afirmativos** — `isActive`, `hasPermission`; evite negação (`notDisabled`, `isNotValid`) que gera dupla negação em `if`.
5. **Coleções no plural**, item no singular (`for (const order of orders)`).
6. **Uma variável, um papel** — variável reatribuída com significados diferentes (não acumuladora) → Split Variable.
7. **Valor de retorno** — nome que deixa claro que é o resultado (convenção do livro: `result`), consistente com o projeto.
8. **Sem ruído** — sufixos/prefixos que nada dizem (`theUser`, `userData`, `userInfo`, `userObj` quando é só `user`); sem notação húngara se o projeto não usa.
9. **Consistente** — o mesmo conceito tem o mesmo nome em todo o diff (não `customer` aqui e `client` ali para a mesma coisa).
10. **Campos de estruturas muito usadas** pesam mais — nome ruim espalha; Rename Field.

Correção: Rename Variable / Rename Field / Split Variable.

### V3. Nomes de constantes

1. **Diz o significado, não o valor** — `MAX_LOGIN_ATTEMPTS = 3`, nunca `THREE = 3` ou `TEN_SECONDS` (o valor muda, o nome mente).
2. **Unidade no nome** quando há (`SESSION_TIMEOUT_MS`, `MAX_UPLOAD_SIZE_BYTES`).
3. **Convenção de caixa do projeto/linguagem** (ex.: `UPPER_SNAKE_CASE` em JS/Java/Python, `PascalCase` em C#/Go exportado) — divergência é achado.
4. **Escopo e local certos** — constante usada por um módulo fica nele; compartilhada fica no lugar onde o projeto já guarda constantes. Arquivo `constants` gigante e sem coesão é achado (agrupe por domínio).
5. **Grupo de constantes relacionadas** (status, tipos, papéis) → enum/tipo próprio em vez de strings/números soltos (Replace Primitive with Object; se dirige comportamento, Replace Type Code with Subclasses).
6. **Não é constante se muda por ambiente** — URLs, chaves, limites por cliente vão para configuração, não para código.

### V4. Números e strings mágicos

Literal mágico = valor cujo significado não é óbvio pelo próprio valor e contexto.

- **Reporte:** números de regra de negócio (`if (age > 17)`, `amount * 0.15`, `audience - 30`), timeouts/limites/tamanhos (`setTimeout(fn, 86400000)`), códigos de status/tipo (`status === 3`, `type === "A"`), strings que identificam estado/papel/chave repetidas, o mesmo literal repetido em vários lugares, índices fixos em arrays (`row[7]`).
- **Não reporte:** `0`, `1`, `-1`, `2` em usos óbvios (início de contagem, incremento, metade, par/ímpar), `100` em percentual evidente, literais em testes que descrevem o cenário, strings de mensagem exibidas uma vez, valores já explicados pelo nome da variável à qual são atribuídos.
- **Correção:** Replace Magic Literal (catálogo online de Fowler) — constante nomeada pelo significado (V3); ou Extract Variable para uso local; grupo de códigos → enum/tipo próprio. Literal repetido em vários lugares sobe a criticidade (vira duplicação).

### V5. Duplicação de código

Procure **dentro do diff e no resto do projeto** (busque por trechos/nomes característicos): o código novo reimplementa algo que já existe?

| Tipo de duplicação | Sinal | Melhoria |
|---|---|---|
| Idêntica | mesmo bloco em 2+ lugares | Extract Function |
| Quase igual, muda só literais/valores | funções gêmeas (`tenPercentRaise`/`fivePercentRaise`) | Parameterize Function |
| Quase igual, linhas intercaladas | mesmos passos em ordem diferente | Slide Statements → Extract Function |
| Mesma lógica de decisão | mesmo `switch`/`if` sobre tipo em vários lugares | Replace Conditional with Polymorphism |
| Em subclasses | métodos/campos iguais nos filhos | Pull Up Method / Pull Up Field / Extract Superclass |
| Em volta das chamadas | as mesmas linhas antes/depois de cada chamada | Move Statements into Function |
| Reimplementa o existente | helper do projeto ou função da stdlib/biblioteca já faz | Replace Inline Code with Function Call / Substitute Algorithm |
| Dado derivado duplicado | valor calculável guardado e sincronizado à mão | Replace Derived Variable with Query |
| Validação/formatação repetida de um primitivo | mesmo `if` de formato de email/CPF/moeda | Replace Primitive with Object |

Criticidade: duplicação que uma mudança plausível precisaria editar em todos os lugares = **Alta**. Duas ocorrências pequenas e estáveis = **Baixa** (regra de três: na terceira, unifique). Código parecido por coincidência, que muda por motivos diferentes, **não** é duplicação — unir criaria acoplamento; diga isso se for o caso.

### V6. Simplificação

Para cada elemento, pergunte: dá para ter menos código, menos indireção ou menos aninhamento com o mesmo comportamento?

| Complexidade desnecessária | Melhoria |
|---|---|
| `if` aninhado profundo, caso normal escondido | Replace Nested Conditional with Guard Clauses |
| Vários `if` levando ao mesmo resultado | Consolidate Conditional Expression |
| Condição longa e obscura | Decompose Conditional / Extract Variable |
| Checagem de nulo/"desconhecido" repetida | Introduce Special Case |
| Loop manual de filtro/mapa/soma | Replace Loop with Pipeline |
| Loop fazendo duas coisas | Split Loop |
| Variável temporária que não diz mais que a expressão | Inline Variable |
| Função/classe que só repassa ou cujo nome = corpo | Inline Function / Inline Class / Remove Middle Man |
| Abstração com uma implementação, parâmetro/gancho "para o futuro", hierarquia sem uso | Collapse Hierarchy / Inline Class / Change Function Declaration / Remove Dead Code |
| Código comentado, função sem chamador, flag que nunca muda | Remove Dead Code |
| Algoritmo enrolado com alternativa direta | Substitute Algorithm |
| `return x ? true : false`, `if (cond) return true; else return false` | retornar a expressão |
| Command/classe para algo que uma função resolve | Replace Command with Function |

Simplificar **não** é encurtar a qualquer custo: código mais curto e mais obscuro (one-liner críptico, encadeamento esperto) é piora. O critério continua sendo leitura e facilidade de mudança.

### V7. Organização e padrão

- Arquivo/módulo no lugar que a estrutura do projeto espera? Camadas respeitadas (ex.: regra de negócio fora de controller/view)?
- Segue as convenções anotadas no passo 2? Divergência do padrão local é achado, mesmo que a alternativa seja "boa" — consistência vale mais que preferência.
- Ordem interna legível (funções públicas/alto nível antes dos detalhes, ou a ordem que o projeto usa)?

## Níveis de criticidade

Todo achado — de qualquer verificação (V1–V7), smell ou lente — recebe **um** nível. O relatório é organizado por nível, do mais crítico para o menos.

| Nível | Critério | Exemplos |
|---|---|---|
| 🔴 **Crítica** | Erro: comportamento incorreto ou frágil visível na leitura, ou nome que mente sobre efeito colateral | caso não tratado, condição invertida, `getX()` que grava/envia, mutação inesperada de argumento |
| 🟠 **Alta** | Teste de mudança falha: mudança plausível exige editar vários lugares, copiar código ou entender o todo para mexer numa parte | duplicação que toda mudança precisa acompanhar, Repeated Switches, Shotgun Surgery, Divergent Change, cálculo misturado com apresentação, Global/Mutable Data com escopo amplo, número mágico de regra de negócio repetido em vários lugares |
| 🟡 **Média** | Atrapalha a leitura de forma recorrente ou foge do padrão do projeto | Long Function, nomes de funções/variáveis/constantes ruins, número mágico isolado de regra de negócio, Long Parameter List, Feature Envy, Data Clumps, Primitive Obsession, divergência das convenções do projeto, falta de testes |
| 🟢 **Baixa** | Atrito pequeno, melhoria local | simplificação local, Lazy Element, loop que poderia ser pipeline, duplicação pequena e estável, nome aceitável mas melhorável |

Na dúvida entre dois níveis, pergunte: "quanto isso custa na próxima mudança provável?" — custo maior, nível maior. Não infle: a maioria dos achados reais é Média ou Baixa.

## Arquivo de saída

- **Local:** raiz do projeto — `git rev-parse --show-toplevel`; fora de repositório git, o diretório de trabalho atual.
- **Nome:** `fowler-review-<YYYY-MM-DD>-<alvo>.md`, onde `<alvo>` é `staged` (opção A) ou `<branch>-vs-<base>` com `/` trocada por `-` (opção B, ex.: `fowler-review-2026-10-22-feat-login-vs-main.md`). Se já existir, acrescente `-2`, `-3`… — nunca sobrescreva uma análise anterior.
- **Conteúdo:** cabeçalho `# Fowler Review — <alvo>` com data, escopo (A: stage / B: `<branch>` vs `<base>` com o hash do merge-base), commit atual (`git rev-parse --short HEAD`), commits analisados (opção B), arquivos analisados com `+linhas/-linhas` e arquivos ignorados. Depois, o relatório completo no formato abaixo, em Markdown.
- Não inclua o próprio relatório no diff analisado em execuções futuras: ele é gerado, não é código.
- Este é o **único** arquivo que a skill cria. Não adicione ao git nem faça commit.
- **No chat:** responda só com o veredito, a contagem por nível de criticidade, os achados 🔴/🟠 (ou os 3 mais graves, se não houver) e o caminho do arquivo.

## Formato do relatório

```
Veredito: <fácil de mudar | aceitável com ressalvas | difícil de mudar> — <1 frase>

Teste de mudança:
- <mudança plausível 1>: <quantos lugares mudam / risco>
- <mudança plausível 2>: ...

Resumo: 🔴 <n> Crítica · 🟠 <n> Alta · 🟡 <n> Média · 🟢 <n> Baixa

## 🔴 Crítica
| # | Local | Categoria | Problema | Melhoria |
|---|---|---|---|---|
| C1 | path:linha | <Erro / V1 nome de função…> | <o que está errado e em que caso falha> | <o que fazer + refactoring pelo nome> |

## 🟠 Alta
| # | Local | Categoria | Problema (qual mudança encarece) | Melhoria |
|---|---|---|---|---|
| A1 | path:linha ↔ path:linha | V5 Duplicação | ... | Parameterize Function — ... |

## 🟡 Média
| # | Local | Categoria | Problema | Melhoria |
|---|---|---|---|---|
| M1 | path:linha | V2 Nome de variável | `data` não revela papel | renomear para `unpaidInvoices` (Rename Variable) |
| M2 | path:linha | V4 Número mágico | `0.15` = alíquota de imposto | constante `TAX_RATE` (Replace Magic Literal) |

## 🟢 Baixa
| # | Local | Categoria | Problema | Melhoria |
|---|---|---|---|---|
| B1 | path:linha | V6 Simplificação | ... | ... |

(Nível sem achados → "Nenhum achado." Categoria = Erro, V1 Nome de função, V2 Nome de variável, V3 Nome de constante, V4 Número mágico, V5 Duplicação, V6 Simplificação, V7 Organização/padrão, ou o nome do smell.)

Cobertura das verificações: V1 ✓ · V2 ✓ · V3 ✓ · V4 ✓ · V5 ✓ · V6 ✓ · V7 ✓ (marque "sem achados" nas que não geraram itens)

Ordem sugerida de ataque: <IDs na ordem — críticas primeiro; dentro do nível, o mais barato e seguro primeiro>

Estrutura-alvo: <como ficaria organizado: funções/módulos/fases e responsabilidades>
Padrão do projeto: <onde segue / onde diverge das convenções existentes>
Pontos fortes: <o que já está bem, curto — só se houver>
Testes: <existem e cobrem? o que falta>
```

Sem achados reais numa seção → diga isso. Não invente achados para preencher.

## Heurísticas do livro para julgar

- Precisou de comentário para dizer *o que* o bloco faz → deveria ser função com esse nome. Comentário de *por quê* é bom.
- Função curta não é sobre número de linhas; é sobre a distância entre o nome (o quê) e o corpo (como).
- Dados e o comportamento que os usa moram juntos; coisas que mudam juntas ficam juntas.
- Grupo de dados que sempre anda junto quer virar objeto.
- Generalidade "para o futuro" sem uso atual é custo, não qualidade.
- Performance não justifica código confuso; só um profiler justifica.
- Julgue pelo impacto em mudanças reais do domínio, não por regras genéricas de estilo.

## Pré-entrega (checklist — rode antes de responder)

- [ ] Perguntei o escopo (stage ou branch vs. base), confirmei a base e analisei **somente** as linhas alteradas nesse diff.
- [ ] Nenhum achado aponta para código não alterado, exceto referências de V5/V7.
- [ ] Anotei o padrão do projeto (passo 2) e comparei contra ele.
- [ ] Fiz o teste de mudança com 2 mudanças concretas do domínio do código.
- [ ] Rodei V1–V7 em **todas** as linhas alteradas e marquei a cobertura de cada uma.
- [ ] Todo achado está em exatamente um nível de criticidade, com ID, categoria e melhoria; níveis sem achados dizem "Nenhum achado".
- [ ] Busquei duplicação também fora do diff (helpers existentes, stdlib).
- [ ] Todo achado tem `path:linha`, problema, impacto e refactoring nomeado.
- [ ] Nenhum achado é só gosto pessoal; nenhum achado inventado; nenhuma "simplificação" que piora a leitura.
- [ ] Incluí a estrutura-alvo de organização.
- [ ] Gravei o relatório completo em `fowler-review-<data>-<alvo>.md` na raiz, sem sobrescrever arquivo existente, e informei o caminho no chat.
- [ ] Nenhum código foi alterado (o relatório é o único arquivo criado).
