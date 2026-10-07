# Catálogo de Filmes e Séries

## 📌 Visão Geral

Este projeto consiste numa API desenvolvida em FastAPI (ou sistema de linha de comando CLI) para gerir um catálogo pessoal de filmes e séries. O objetivo do sistema é permitir que o utilizador acompanhe o progresso de visualização de séries, compare avaliações entre mídias, gira listas personalizadas e consulte relatórios de consumo. A modelação do sistema é orientada a objetos (POO), enfatizando conceitos como herança, encapsulamento, validações e composição.

## 🚀 Funcionalidades Principais

* **Cadastro de Mídias**: Permite o registo de filmes e séries com atributos como título, tipo, género, ano, duração e classificação indicativa. O sistema impede a duplicidade de mídias que possuam o mesmo título, tipo e ano.


* **Gestão de Séries e Episódios**: Suporta o registo de temporadas e episódios para a entidade Série. O sistema marca automaticamente a série com o status de "ASSISTIDA" assim que todos os seus episódios estiverem concluídos.


* **Sistema de Avaliações**: Os utilizadores podem avaliar filmes e episódios atribuindo uma nota numérica de 0 a 10. O sistema calcula de forma automática a nota média das séries e a nota geral do catálogo.


* **Histórico e Listas Personalizadas**: Regista a data e hora de conclusão de cada mídia. Permite criar listas personalizadas (ex: "Para assistir", "Favoritos") até um limite definido nas configurações e adicionar/remover mídias das mesmas.


* **Relatórios e Estatísticas**: Geração de relatórios que incluem a média de notas por género, o tempo total assistido por tipo de mídia, o Top 10 das mídias mais bem avaliadas e as séries com o maior número de episódios assistidos. Os relatórios consideram apenas mídias com o status "ASSISTIDO".


* **Configurações Dinâmicas**: Leitura de parâmetros através do ficheiro `settings.json`, que define a nota mínima para uma mídia ser "recomendada", o limite de listas por utilizador e o multiplicador de duração para conversão de tempo.



## 📂 Estrutura de Arquivos e Diretórios

A arquitetura do projeto está organizada em camadas, separando a interface, as regras de negócio e os modelos de domínio:
```
catalogo_filmes/
│
├── main.py                  # Ponto de entrada da aplicação FastAPI
├── dados.py                 # Módulo de persistência 
├── settings.json            # Arquivo de configurações
├── README.md                # Arquivo com documentação e diagrama Mermaid
├── requirements.txt         # Dependências do projeto
│
├── api/                     # Camada de Interface (FastAPI)
│   ├── __init__.py
│   └── rotas.py             
│
├── models/                  # Camada de Domínio (Classes principais)
│   ├── __init__.py
│   ├── enums.py             # StatusVisualizacao e TipoMidia
│   ├── exceptions.py        # Exceções customizadas (ValorInvalidoError, etc.)
│   ├── mixins.py            # AvaliavelMixin e SerializavelMixin
│   ├── midia.py             # Midia, Filme, Serie, Temporada, Episodio
│   └── usuario.py           # Usuario, ListaPersonalizada, RegistroHistorico
│
├── services/                # Camada de Regras de Negócio
│   ├── __init__.py
│   ├── relatorio.py         # RelatorioService (Cálculos de médias e top 10)
│   └── configuracao.py      # Classe Configuracao (Lê o settings.json)
│
└── tests/                   # Diretório de testes automatizados (pytest)
    ├── __init__.py
    ├── test_midia.py        # Testes das regras de negócio de Mídias/Episódios
    └── test_relatorios.py   # Testes dos cálculos matemáticos
```

## 📊 Diagrama de Classes (UML)

Abaixo encontra-se a representação da modelação orientada a objetos do projeto, ilustrando os relacionamentos de herança, composição e agregação:

```mermaid
classDiagram
    direction TB

    class StatusVisualizacao {
        <<enumeration>>
        NAO_ASSISTIDO
        ASSISTINDO
        ASSISTIDO
    }

    class TipoMidia {
        <<enumeration>>
        FILME
        SERIE
    }

    class DominioError {
        <<exception>>
    }
    class ValorInvalidoError {
        <<exception>>
    }
    class EstadoInvalidoError {
        <<exception>>
    }

    DominioError <|-- ValorInvalidoError
    DominioError <|-- EstadoInvalidoError

    class AvaliavelMixin {
        <<mixin>>
        #float nota
        +nota() float
        +avaliar(valor: float) void
    }

    class SerializavelMixin {
        <<mixin>>
        +to_dict() dict
    }

    class Midia {
        <<abstract>>
        #String titulo
        #TipoMidia tipo
        #String genero
        #int ano
        #String classificacao_indicativa
        #List~String~ elenco
        #StatusVisualizacao status
        #float nota
        #datetime data_conclusao
        +titulo() String
        +genero() String
        +ano() int
        +tipo() TipoMidia
        +nota() float
        +status() StatusVisualizacao
        +data_conclusao() datetime
        +duracao_minutos()* int
        +avaliar(valor: float) void      
        +alterar_status(novo_status: StatusVisualizacao) void
        +__str__() String
        +__repr__() String
        +__eq__(outro: Object) bool
        +__lt__(outro: Object) bool
    }

    class Filme {
        -int duracao_minutos
        +duracao_minutos() int
        +__str__() String
    }

    class Serie {
        -List~Temporada~ temporadas
        +duracao_minutos() int
        +nota() float
        +atualizar_status() void
        +adicionar_temporada(temporada: Temporada) void
        +__len__() int
        +__str__() String
    }

    class Temporada {
        -int numero
        -List~Episodio~ episodios
        +numero() int
        +duracao_minutos() int
        +adicionar_episodio(episodio: Episodio) void
        +calcular_nota_media() float
        +__len__() int
    }

    class Episodio {
        -int numero_temporada
        -int numero_episodio
        -String titulo
        -int duracao_minutos
        -date data_lancamento
        -StatusVisualizacao status
        -float nota
        +titulo() String
        +numero_temporada() int
        +numero_episodio() int
        +duracao_minutos() int
        +status() StatusVisualizacao
        +nota() float
        +avaliar(valor: float) void
        +alterar_status(novo_status: StatusVisualizacao) void
    }

    class Usuario {
        -String id
        -String nome
        -String email
        -List~ListaPersonalizada~ listas
        -List~RegistroHistorico~ historico
        +criar_lista(nome: String) ListaPersonalizada
        +adicionar_favorito(midia: Midia) void
    }

    class ListaPersonalizada {
        -String nome
        -List~Midia~ midias
        +adicionar_midia(midia: Midia) void
        +remover_midia(midia: Midia) void
    }

    class RegistroHistorico {
        -datetime data_hora
        -Midia midia
        +data_hora() datetime
    }

    %% Herança e Mixins
    Midia <|-- Filme : Herança
    Midia <|-- Serie : Herança

    %% Agregação e Composição
    Serie "1" o-- "*" Temporada : Agrega
    Temporada "1" *-- "*" Episodio : Contém (Composição)

    %% Uso de Enums
    Midia --> TipoMidia : possui
    Midia --> StatusVisualizacao : possui
    Episodio --> StatusVisualizacao : possui

    %% Relacionamentos do Usuário
    Usuario "1" *-- "*" ListaPersonalizada : gerencia
    Usuario "1" *-- "*" RegistroHistorico : registra
    ListaPersonalizada "*" o-- "*" Midia : agrupa
    RegistroHistorico --> Midia : refere-se

```


## 🛠️ Como Executar o Projeto

### Pré-requisitos
* Python 3.10+

### Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/edson-santos0077/catalogo-de-filmes-e-series.git
   cd catalogo-de-filmes-e-series
   ```
   
   
## 🧪 Executando os Testes Automatizados

Para rodar a suíte de testes com o `pytest`, execute:
```bash
py -m pytest -v
```
