---
name: commit-message
description: Gera uma mensagem de commit semântica (Conventional Commits) a partir das mudanças em staged. Se não houver nada em staged, usa as mudanças não commitadas (working tree). NUNCA faz commit nem push — apenas produz a mensagem para o usuário copiar. Use quando o usuário pedir para "gerar/criar/escrever uma mensagem de commit", "commit message", "sugerir mensagem de commit" ou invocar /commit-message.
disable-model-invocation: false
metadata:
  author: rafael.penha@nagro.com.br
  version: '1.0.0'
---

# Gerador de Mensagem de Commit Semântica

Analisa as mudanças do repositório e produz **uma mensagem de commit** no padrão
[Conventional Commits](https://www.conventionalcommits.org). O resultado é apenas
texto entregue ao usuário — a decisão de commitar é dele.

## Regra inviolável

**NUNCA execute `git commit`, `git push`, `git add`, `git reset` ou qualquer comando
que altere o estado do repositório.** Esta skill é somente leitura. Se o usuário pedir
para commitar dentro desta skill, responda que a skill só gera a mensagem e que ele deve
rodar o commit manualmente (ou pedir explicitamente fora da skill). Use apenas comandos
`git` de leitura: `git status`, `git diff`, `git log`.

## Passos

1. **Verifique se há mudanças em staged:**
   ```
   git diff --cached --stat
   ```
   - Se houver saída → a fonte da análise é o **staged** (`git diff --cached`).
   - Se estiver vazio → verifique o working tree:
     ```
     git diff --stat
     ```
     - Se houver saída → a fonte é o **working tree** (`git diff`).
     - Se ambos vazios → informe que não há mudanças para analisar e pare.

2. **Leia o diff completo da fonte escolhida** (`git diff --cached` ou `git diff`) para
   entender o que mudou de fato — não confie só nos nomes de arquivo. Para arquivos novos
   não rastreados que só aparecem no working tree, use `git status --porcelain` e leia o
   conteúdo com o Read tool se necessário.

3. **Consulte o estilo do repositório** para casar com a convenção local:
   ```
   git log --oneline -20
   ```
   Observe idioma das mensagens, uso de escopo, tipos usados, e siga o mesmo padrão.

4. **Monte a mensagem** no formato:
   ```
   <tipo>(<escopo opcional>): <descrição no imperativo, minúsculo, sem ponto final>

   <corpo opcional: o quê e o porquê, uma linha em branco após o título>

   <rodapé opcional: BREAKING CHANGE:, refs de issue, etc.>
   ```

## Tipos (Conventional Commits)

| Tipo       | Quando usar                                                        |
|------------|--------------------------------------------------------------------|
| `feat`     | Nova funcionalidade                                                 |
| `fix`      | Correção de bug                                                     |
| `refactor` | Mudança de código sem alterar comportamento externo                 |
| `perf`     | Melhoria de performance                                             |
| `test`     | Adição/ajuste de testes                                             |
| `docs`     | Somente documentação                                                |
| `style`    | Formatação, sem mudança de lógica                                   |
| `build`    | Build system, dependências                                          |
| `ci`       | Configuração de CI                                                  |
| `chore`    | Tarefas de manutenção que não se encaixam acima                     |

## Diretrizes

- **Título ≤ 72 caracteres**, imperativo ("adiciona", não "adicionado"/"adicionando"),
  primeira letra minúscula, sem ponto final.
- Siga o **idioma predominante** do histórico do repositório (se os commits recentes são
  em português, escreva em português).
- Use **escopo** quando fizer sentido e o repositório já usar (ex.: módulo/pasta afetada).
- Se as mudanças abrangem propósitos distintos, **sinalize ao usuário** que talvez devam
  ser commits separados e sugira uma mensagem por grupo.
- Inclua **corpo** apenas quando agregar contexto real (motivo da mudança, impacto).
- Marque `BREAKING CHANGE:` no rodapé quando houver quebra de compatibilidade.

## Saída

Entregue ao usuário:

1. Qual fonte foi usada (**staged** ou **working tree**) e quantos arquivos.
2. O **comando `git commit` completo**, dentro de um bloco de código, pronto para
   copiar e colar. Este é o item principal da saída.
   - Título simples (sem corpo):
     ```
     git commit -m "feat(escopo): descrição no imperativo"
     ```
   - Com corpo e/ou rodapé, use múltiplos `-m` (cada `-m` vira um parágrafo):
     ```
     git commit -m "feat(escopo): descrição no imperativo" \
       -m "Corpo explicando o quê e o porquê da mudança." \
       -m "BREAKING CHANGE: descreva a quebra de compatibilidade."
     ```
   - Escape corretamente aspas duplas dentro da mensagem, ou prefira aspas simples
     quando o texto contiver `"`.
   - Se o usuário estava no fluxo de **working tree** (nada em staged) e quiser
     incluir tudo, ofereça também a variante com `git commit -a -m "..."` — deixando
     claro que `-a` adiciona apenas arquivos já rastreados.

**Lembrete: apenas exiba o comando. NUNCA execute o `git commit`.** A execução é
responsabilidade do usuário.
