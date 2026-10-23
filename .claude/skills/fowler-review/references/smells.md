# Code smells (Fowler, cap. 3) — sinais e melhoria

Para cada smell: **Sinal** = o que procurar no código. **Por que dói** = qual mudança/leitura encarece. **Melhoria** = refactorings (ver `catalog.md`).

## 1. Mysterious Name
- **Sinal:** precisa ler o corpo para saber o que função/variável/campo é; nomes genéricos (`data`, `tmp`, `handle`, `x`), abreviações obscuras.
- **Por que dói:** cada leitor redescobre o significado. Nome difícil de escolher costuma indicar responsabilidade confusa.
- **Melhoria:** Change Function Declaration (renomear), Rename Variable, Rename Field.

## 2. Duplicated Code
- **Sinal:** mesma estrutura em dois ou mais lugares, idêntica ou quase.
- **Por que dói:** toda mudança precisa achar e atualizar todas as cópias; leitor compara cópias para ver diferenças.
- **Melhoria:** Extract Function; Slide Statements para aproximar o que é parecido antes de extrair; Pull Up Method se as cópias estão em subclasses.

## 3. Long Function
- **Sinal:** função faz vários "o quê"; blocos precedidos de comentário explicando o bloco; condicionais e loops grandes no meio.
- **Por que dói:** precisa entender tudo para mudar uma parte. O problema é a distância entre intenção e implementação, não a contagem de linhas.
- **Melhoria:** Extract Function (quase sempre); Replace Temp with Query para liberar a extração; Introduce Parameter Object / Preserve Whole Object para parâmetros; Decompose Conditional; Split Loop; Replace Function with Command em último caso.

## 4. Long Parameter List
- **Sinal:** muitos parâmetros; parâmetros deriváveis de outro; flags booleanas; o mesmo grupo repetido em várias funções.
- **Por que dói:** chamadas confusas, ordem errada passa despercebida.
- **Melhoria:** Replace Parameter with Query, Preserve Whole Object, Introduce Parameter Object, Remove Flag Argument, Combine Functions into Class.

## 5. Global Data
- **Sinal:** variável global, estática de classe ou singleton mutável acessado de qualquer lugar.
- **Por que dói:** qualquer código pode alterar; impossível saber quem mexeu.
- **Melhoria:** Encapsulate Variable primeiro, depois reduzir o escopo (mover para módulo/classe).

## 6. Mutable Data
- **Sinal:** estrutura alterada em vários pontos; variável reatribuída com significados diferentes; valor calculável guardado e mantido em sincronia manualmente.
- **Por que dói:** uma alteração aqui quebra quem esperava outro valor ali.
- **Melhoria:** Encapsulate Variable, Split Variable, Slide Statements + Extract Function (isolar o código sem efeito colateral), Separate Query from Modifier, Remove Setting Method, Replace Derived Variable with Query, Combine Functions into Class/Transform, Change Reference to Value.

## 7. Divergent Change
- **Sinal:** um mesmo módulo muda por motivos diferentes ("para novo banco mexo nestas 3 funções, para novo produto naquelas 4").
- **Por que dói:** toda mudança exige entender contextos não relacionados.
- **Melhoria:** Split Phase (se os contextos formam sequência), Move Function, Extract Function, Extract Class.

## 8. Shotgun Surgery
- **Sinal:** uma única mudança exige pequenas edições em muitos módulos.
- **Por que dói:** fácil esquecer um lugar.
- **Melhoria:** Move Function, Move Field, Combine Functions into Class/Transform, Split Phase; Inline Function/Class para juntar e depois re-extrair.

## 9. Feature Envy
- **Sinal:** função que usa mais dados/métodos de outro módulo que do próprio (vários getters do outro objeto).
- **Por que dói:** mudança nos dados do outro módulo quebra código espalhado.
- **Melhoria:** Move Function (com Extract Function da parte invejosa antes). Regra: fica com o módulo que tem a maior parte dos dados.

## 10. Data Clumps
- **Sinal:** os mesmos 3–4 dados juntos em campos e assinaturas. Teste: removendo um, os outros fazem sentido?
- **Por que dói:** listas longas repetidas; comportamento desses dados fica espalhado.
- **Melhoria:** Extract Class, Introduce Parameter Object, Preserve Whole Object.

## 11. Primitive Obsession
- **Sinal:** dinheiro como número, telefone/CPF/status como string, intervalos como dois números, código de tipo em string/enum dirigindo lógica.
- **Por que dói:** validação e formatação duplicadas; unidades misturadas.
- **Melhoria:** Replace Primitive with Object; Replace Type Code with Subclasses + Replace Conditional with Polymorphism; Extract Class / Introduce Parameter Object para grupos.

## 12. Repeated Switches
- **Sinal:** o mesmo `switch`/cadeia de `if` sobre o mesmo tipo aparece em vários lugares. (Um switch isolado é aceitável.)
- **Por que dói:** novo caso exige achar e editar todos.
- **Melhoria:** Replace Conditional with Polymorphism.

## 13. Loops
- **Sinal:** loop manual fazendo filtro/transformação/acúmulo onde a linguagem tem pipeline (map/filter/reduce).
- **Por que dói:** leitor precisa simular o loop para saber o que entra e o que sai.
- **Melhoria:** Replace Loop with Pipeline (e Split Loop se faz mais de uma coisa).

## 14. Lazy Element
- **Sinal:** função cujo nome diz o mesmo que o corpo; classe que é praticamente uma função; hierarquia sem razão.
- **Por que dói:** indireção sem ganho.
- **Melhoria:** Inline Function, Inline Class, Collapse Hierarchy.

## 15. Speculative Generality
- **Sinal:** ganchos, parâmetros, classes abstratas, configurações "para o futuro" sem uso; únicos usuários são testes.
- **Por que dói:** complexidade a manter sem benefício.
- **Melhoria:** Collapse Hierarchy, Inline Function/Class, Change Function Declaration (remover parâmetro), Remove Dead Code.

## 16. Temporary Field
- **Sinal:** campo preenchido só em certas situações; fica vazio/nulo no resto.
- **Por que dói:** leitor espera que todo campo importe sempre.
- **Melhoria:** Extract Class para os campos órfãos + Move Function; Introduce Special Case para o caso "sem valor".

## 17. Message Chains
- **Sinal:** `a.getB().getC().getD()` ou sequência de temporários navegando objetos.
- **Por que dói:** cliente acoplado à estrutura de navegação.
- **Melhoria:** Hide Delegate; ou Extract Function do que usa o resultado + Move Function para baixo na cadeia.

## 18. Middle Man
- **Sinal:** classe em que boa parte dos métodos só repassa para outra.
- **Por que dói:** indireção sem valor.
- **Melhoria:** Remove Middle Man, Inline Function, Replace Superclass/Subclass with Delegate.

## 19. Insider Trading
- **Sinal:** módulos trocando muitos dados internos entre si; subclasses que conhecem demais o pai.
- **Por que dói:** acoplamento alto; mudar um quebra o outro.
- **Melhoria:** Move Function, Move Field, Hide Delegate, Replace Subclass/Superclass with Delegate.

## 20. Large Class
- **Sinal:** muitos campos (prefixos/sufixos comuns indicam subgrupos), muito código, clientes usando subconjuntos distintos.
- **Por que dói:** duplicação interna e responsabilidades misturadas.
- **Melhoria:** Extract Class, Extract Superclass, Replace Type Code with Subclasses.

## 21. Alternative Classes with Different Interfaces
- **Sinal:** classes intercambiáveis em conceito, mas com métodos de nomes/assinaturas diferentes.
- **Por que dói:** impede substituição; duplica chamadores.
- **Melhoria:** Change Function Declaration, Move Function, Extract Superclass.

## 22. Data Class
- **Sinal:** só campos e getters/setters; outras classes manipulam esses dados em detalhe.
- **Por que dói:** comportamento no lugar errado, espalhado pelos clientes.
- **Melhoria:** Encapsulate Record, Remove Setting Method, Move Function / Extract Function para dentro da classe. Exceção: registro imutável de resultado (ex. dado intermediário de Split Phase) é aceitável.

## 23. Refused Bequest
- **Sinal:** subclasse ignora a maior parte do que herda. Forte se recusa a *interface* do pai, fraco se só ignora implementação.
- **Por que dói:** hierarquia mente sobre o que as classes são.
- **Melhoria:** Push Down Method/Field (caso fraco, só se causar confusão); Replace Subclass/Superclass with Delegate (caso forte).

## 24. Comments (como desodorante)
- **Sinal:** comentários explicando *o que* um bloco confuso faz.
- **Por que dói:** o comentário compensa código ruim e envelhece.
- **Melhoria:** Extract Function (nome no lugar do comentário), Change Function Declaration (renomear), Introduce Assertion (para regras de estado). Comentário de *por quê* ou de incerteza é bom — não reporte.
