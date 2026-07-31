# Brief do subagent de auditoria

O subagent começa frio: não viu a conversa, não conhece o projeto, não sabe o que já foi corrigido antes. Tudo que ele precisa está no brief — e **só** o que ele precisa, porque contexto irrelevante é o que faz um agente sair do escopo.

Ele é **somente leitura**. Não corrige nada: devolve a tabela, e quem orquestra a triagem aplica as correções.

**Preencha os `<...>` com o Perfil do projeto levantado na Fase 0.** Um brief com os placeholders intactos manda o agente adivinhar, e ele adivinha.

```
Você está AUDITANDO a documentação deste repositório contra o código que existe
hoje. Sua missão não é confirmar que a documentação está boa — é DERRUBAR cada
afirmação que ela faz. Assuma que há mentira e procure-a.

NÃO EDITE NENHUM ARQUIVO. Você devolve uma tabela; outro agente corrige.

LEIA, NESTA ORDEM:
1. <arquivo de estado do projeto> — o estado atual, as pendências, os bloqueios
2. <arquivo de roadmap> — o escopo de cada milestone e o que ele diz estar pronto
3. O status de CADA feature — <caminho dos arquivos de task, ou como consultar
   o rastreador externo, conforme o Perfil do projeto>
4. TODOS os arquivos de <caminho do retrato do código>   ← NÃO PULE
5. <regras do repositório: AGENTS.md / CLAUDE.md / CONTRIBUTING.md>

⚠️ O item 4 é o mais esquecido e o mais perigoso. Numa auditoria real, varrer só
estado/roadmap/tasks achou 5 divergências; incluir os documentos de arquitetura e
convenções achou 24 — entre elas um guia de convenções cujos exemplos de código
apontavam todos para uma feature removida um milestone antes, e um documento de
arquitetura afirmando que não havia versionamento de banco, sobre um banco com
oito migrações versionadas. São os arquivos que dizem ao agente COMO escrever
código: quem obedecer copia exemplo que não compila.

PARA CADA AFIRMAÇÃO SOBRE O CÓDIGO, confira no CÓDIGO — não no outro documento:
- o símbolo citado existe? (grep pelo nome exato)
- o arquivo ou caminho citado existe? (liste, não deduza)
- o ponto de entrada citado ainda está registrado? (grep no registro real)
- o exemplo de código copiaria e rodaria hoje?

CACE ESPECIFICAMENTE O PADRÃO "NÚMERO COPIADO PARA A PROSA".
Todo número escrito em prosa envelhece e ninguém percebe. Meça cada um AGORA,
com o comando, e compare:
- contagens de teste na documentação  vs.  <comando de teste deste projeto>
- "a próxima migração/versão é a N"   vs.  a lista real no código
- contagens de chave de tradução      vs.  as chaves contadas nos arquivos
- tamanhos de artefato, contagens de task, contagens de requisito
O baseline de teste é o pior caso: ele costuma ser usado como GATE, então a prosa
errada vira critério de aprovação errado.

GATES DESTE PROJETO (rode e ANOTE O NÚMERO, não "passou"):
<lista de comandos descobertos na Fase 0>

DEVOLVA UMA TABELA, uma linha por divergência:

| Afirmação (verbatim) | Arquivo:linha | O que o código diz | Evidência (comando + saída) | Gravidade |

Gravidade:
- ALTA   — um agente que obedecer escreve código errado (exemplo quebrado,
           número de versão/migração já gasto, baseline de gate errado)
- MÉDIA  — descreve estado errado, mas não induz a erro de código
- BAIXA  — impreciso, sem consequência prática

REGRAS:
- Evidência é comando + saída. "Verifiquei que não existe" não é evidência.
- Se você não conseguiu conferir uma afirmação, ela entra na tabela como
  "NÃO VERIFICADO" com o motivo — nunca como "ok".
- Não proponha correção de redação. Diga o que o código diz; quem orquestra
  decide como escrever.
- Checkbox dentro de uma task já concluída é critério de aceitação, não
  pendência. Um grep ingênuo devolve centenas de fantasmas.
- Não toque em dados reais (banco local, workspace, cache do usuário). Se
  precisar ler um, trabalhe sobre uma cópia em diretório temporário.
```

---

## Depois que a tabela volta

Quem orquestra aplica as correções — é bookkeeping, e é o produto do próprio raciocínio dele:

- Requisito ou pendência que perdeu o objeto é **riscado com o motivo**, nunca apagado. Nomeie o que o revogou.
- Marque como **"sem objeto, não verificado"**, nunca como "feito".
- Se o escopo de um milestone mudou, roadmap e documento de estado mudam juntos.
- Todo número reescrito vem da medição desta triagem, e o comando que o mediu vai para a seção **Perfil do projeto** do `TRIAGE.md`.
- Se as regras do repositório contradisserem qualquer coisa acima, **as regras do repositório vencem** — e a contradição vira uma linha do relatório.
