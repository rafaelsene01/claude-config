# Catálogo de refactorings (Fowler, caps. 6–12) — para recomendar melhorias

Cada item: **o que faz** · *recomende quando*. Use o nome exato no achado. Inversos indicados com ⇄.

## Básicos (cap. 6)
- **Extract Function** ⇄ Inline Function — transforma um trecho em função nomeada pela intenção · *bloco precisa de comentário, função longa, código duplicado.*
- **Inline Function** — substitui a chamada pelo corpo · *o corpo é tão claro quanto o nome; indireção sem valor; antes de reagrupar código mal dividido.*
- **Extract Variable** ⇄ Inline Variable — nomeia uma expressão complexa · *expressão difícil de ler dentro de condição/cálculo.*
- **Inline Variable** — remove variável que não diz mais que a expressão · *temp atrapalha uma extração ou é redundante.*
- **Change Function Declaration** (rename / add / remove parameter) — muda nome ou parâmetros; em APIs publicadas, cria a nova, deixa a antiga delegando e deprecia · *nome não revela propósito; parâmetro inútil; parâmetro acopla a função a um tipo desnecessário.*
- **Encapsulate Variable** — acesso a dado amplamente usado passa por funções · *dado global/mutável de escopo grande.*
- **Rename Variable** — · *nome não revela papel.*
- **Introduce Parameter Object** — agrupa parâmetros que andam juntos num objeto · *data clump em assinaturas.*
- **Combine Functions into Class** — junta funções que operam sobre os mesmos dados numa classe · *várias funções recebem o mesmo registro.*
- **Combine Functions into Transform** — uma função recebe o dado bruto e devolve cópia enriquecida com os derivados · *cálculos derivados espalhados; dado só de leitura.*
- **Split Phase** — separa o código em fases sequenciais com uma estrutura de dados intermediária (ex.: calcular → formatar; parsear → processar) · *mesma função mistura duas preocupações; dois formatos de saída para o mesmo cálculo.*

## Encapsulamento (cap. 7)
- **Encapsulate Record** — troca registro/dicionário cru por classe · *dado estruturado mutável acessado em detalhe por muitos.*
- **Encapsulate Collection** — getter devolve cópia/visão só leitura; adição/remoção por métodos · *clientes alteram a coleção interna diretamente.*
- **Replace Primitive with Object** — cria tipo de valor para um primitivo do domínio · *primitive obsession; validação/formatação repetida.*
- **Replace Temp with Query** — move o cálculo do temp para uma função · *temp impede extração; mesmo cálculo usado em vários lugares.*
- **Extract Class** ⇄ Inline Class — separa um subconjunto de campos/métodos em nova classe · *large class; campos com prefixo comum; responsabilidades distintas.*
- **Inline Class** — absorve classe que faz pouco · *lazy class; antes de redistribuir responsabilidades.*
- **Hide Delegate** ⇄ Remove Middle Man — servidor expõe método que delega, escondendo o objeto interno · *message chains.*
- **Remove Middle Man** — clientes falam direto com o delegado · *classe virou só repassadora.*
- **Substitute Algorithm** — troca o algoritmo inteiro por um mais claro · *existe forma muito mais simples (ex.: função da biblioteca).*

## Movendo funcionalidades (cap. 8)
- **Move Function** — leva a função para o módulo cujos dados ela mais usa · *feature envy; função no contexto errado.*
- **Move Field** — leva o campo para onde é usado junto · *campo sempre passado/alterado junto com dados de outra estrutura.*
- **Move Statements into Function** ⇄ Move Statements to Callers — linhas sempre repetidas junto da chamada vão para dentro da função · *duplicação em volta das chamadas.*
- **Move Statements to Callers** — parte da função que varia por chamador sai dela · *função faz algo que só alguns chamadores querem.*
- **Replace Inline Code with Function Call** — usa função existente (inclusive da biblioteca) no lugar de código manual · *reimplementação do que já existe.*
- **Slide Statements** — aproxima linhas relacionadas (declaração junto do uso) · *código relacionado intercalado; preparação para extração.*
- **Split Loop** — um loop fazendo duas coisas vira dois · *loop acumula valores não relacionados.*
- **Replace Loop with Pipeline** — loop vira map/filter/reduce · *loop manual de filtro/transformação.*
- **Replace Magic Literal** (catálogo online de Fowler, não está no livro impresso) — literal com significado vira constante nomeada · *número/string de regra de negócio ou repetido sem explicação.*
- **Remove Dead Code** — apaga código sem uso (o versionamento guarda o histórico) · *código comentado, funções sem chamadores, flags que nunca mudam.*

## Organizando dados (cap. 9)
- **Split Variable** — uma variável por responsabilidade · *variável (não acumuladora) reatribuída com significados diferentes; parâmetro reatribuído.*
- **Rename Field** — · *campo com nome ruim, principalmente em estruturas muito usadas.*
- **Replace Derived Variable with Query** — calcula sob demanda em vez de guardar e sincronizar · *valor derivável mantido manualmente.*
- **Change Reference to Value** ⇄ Change Value to Reference — objeto interno imutável, substituído inteiro · *objeto pequeno alterado no lugar; igualdade por conteúdo faz sentido.*
- **Change Value to Reference** — instâncias compartilhadas via repositório · *várias cópias do mesmo conceito precisam ver a mesma atualização.*

## Simplificando condicionais (cap. 10)
- **Decompose Conditional** — extrai condição e cada ramo em funções nomeadas · *condição complexa cujo significado não é óbvio.*
- **Consolidate Conditional Expression** — junta checagens que levam ao mesmo resultado · *sequência de ifs com o mesmo retorno.*
- **Replace Nested Conditional with Guard Clauses** — trata casos especiais com retorno antecipado · *aninhamento profundo; caso normal escondido.*
- **Replace Conditional with Polymorphism** — cada ramo vira método numa subclasse/estratégia · *repeated switches sobre o mesmo tipo.*
- **Introduce Special Case** (Null Object) — objeto para o caso especial, com comportamento padrão · *mesma checagem de nulo/"desconhecido" repetida em vários lugares.*
- **Introduce Assertion** — explicita uma suposição sobre o estado · *código assume condição que só um comentário (ou ninguém) documenta.*

## Refatorando APIs (cap. 11)
- **Separate Query from Modifier** — função que retorna valor não deve ter efeito colateral; separa as duas · *"get" que também altera estado.*
- **Parameterize Function** — funções quase iguais viram uma com parâmetro · *duplicação diferindo só por literais.*
- **Remove Flag Argument** — uma função explícita por valor da flag · *parâmetro booleano/enum que escolhe comportamento passado como literal.*
- **Preserve Whole Object** — passa o objeto em vez de vários campos dele · *chamador extrai campos só para passá-los.*
- **Replace Parameter with Query** ⇄ Replace Query with Parameter — função obtém o valor sozinha · *parâmetro derivável de outro parâmetro.*
- **Replace Query with Parameter** — dependência vira parâmetro, deixando a função pura · *função depende de global/estado que dificulta teste.*
- **Remove Setting Method** — valor definido só no construtor · *campo que não deveria mudar após criação.*
- **Replace Constructor with Factory Function** — · *construtor limitado (nome fixo, tipo fixo de retorno).*
- **Replace Function with Command** ⇄ Replace Command with Function — função complexa vira objeto com execute · *função longa com muitos temps difíceis de extrair; necessidade de undo/estágios.*
- **Replace Command with Function** — · *command simples demais para justificar a classe.*

## Herança (cap. 12)
- **Pull Up Method / Pull Up Field / Pull Up Constructor Body** ⇄ Push Down — move o comum das subclasses para o pai · *duplicação entre subclasses.*
- **Push Down Method / Push Down Field** — move para as subclasses que usam · *membro do pai relevante só para algumas subclasses.*
- **Replace Type Code with Subclasses** ⇄ Remove Subclass — código de tipo vira subclasses · *tipo dirige comportamento em vários lugares ou campos só valem para certos tipos.*
- **Remove Subclass** — · *subclasses fazem tão pouco que não se justificam.*
- **Extract Superclass** — cria pai comum para classes parecidas · *duas classes com dados/métodos semelhantes.*
- **Collapse Hierarchy** — funde pai e filho · *quase não diferem.*
- **Replace Subclass with Delegate** — subclasses viram objeto delegado (State/Strategy) · *mais de um eixo de variação; tipo muda em tempo de execução; herança acoplando demais.*
- **Replace Superclass with Delegate** — herança vira composição · *subclasse não é de fato um tipo do pai; usa só parte da interface.*

## Exemplo de estrutura-alvo (cap. 1)

Ponto de partida típico: uma função longa que percorre itens, calcula valor por tipo com `switch`, acumula totais e monta texto, tudo junto.

Organização-alvo que o livro chega:
1. **Fase de cálculo** (Split Phase): uma função produz um objeto de dados com tudo já calculado (itens enriquecidos, totais) — sem formatação.
2. **Fase de apresentação**: funções de render (texto, HTML…) consomem só esse objeto. Novo formato = nova função de render, sem tocar no cálculo.
3. **Variação por tipo** (Replace Conditional with Polymorphism): uma classe calculadora por tipo; novo tipo = nova classe, sem editar switches.
4. **Funções pequenas com nomes de intenção** (Extract Function, Replace Temp with Query, Split Loop, Replace Loop with Pipeline) para cada cálculo e total.

Use esse padrão como referência ao descrever a estrutura-alvo de código com forma parecida (processa coleção → calcula → formata).
