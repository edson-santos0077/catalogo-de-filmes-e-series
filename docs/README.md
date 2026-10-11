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
├── data/                        # Arquivos locais e de persistência
│   └── catalogo.db              # Arquivo do banco de dados SQLite (gerado automaticamente)
│
├── docs/                        # Documentação do projeto
│   └── README.md                # Documentação principal e diagramas Mermaid
│
├── requirements.txt             # Dependências do projeto (FastAPI, SQLAlchemy, etc.)
├── .gitignore                   # Ficheiros ignorados pelo Git (.env, __pycache__, catalogo.db)
│
├── src/                         # Código-fonte da aplicação (Encapsulamento)
│   ├── main.py                  # Ponto de entrada do FastAPI (agora protegido dentro de src)
│   │
│   ├── api/                     # Camada de Interface (Rotas HTTP)
│   │   ├── __init__.py
│   │   ├── rotas_midias.py
│   │   ├── rotas_usuarios.py
│   │   └── schemas.py           # Validações Pydantic
│   │
│   ├── core/                    # Configurações globais do sistema
│   │   ├── __init__.py
│   │   ├── configuracao.py      # Lógica para ler e validar o settings.json
│   │   └── settings.json        # Arquivo de parâmetros dinâmicos
│   │
│   ├── models/                  # Camada de Domínio (As suas classes POO)
│   │   ├── __init__.py
│   │   ├── enums.py
│   │   ├── exceptions.py
│   │   ├── filme.py
│   │   ├── mixins.py
│   │   ├── midia.py
│   │   ├── serie.py
│   │   └── usuario.py
│   │
│   ├── repositories/            # Camada de Acesso a Dados
│   │   ├── __init__.py
│   │   ├── database.py          # Configuração do ORM e conexão SQLite (substitui o antigo dados.py solto)
│   │   ├── midia_repository.py
│   │   └── usuario_repository.py
│   │
│   └── services/                # Regras de Negócio e Casos de Uso
│       ├── __init__.py
│       └── relatorio.py         # Cálculos de médias e estatísticas
│
└── tests/
    ├── __init__.py
    ├── conftest.py              # Fixtures globais (ex: banco SQLite em memória para os testes)
    ├── test_api.py              # Testes de integração dos endpoints
    ├── test_midia.py            # Testes unitários puros das classes (sem banco de dados)
    └── test_relatorios.py       # Testes da lógica de relatórios
```

## 📊 Diagrama de Classes (UML)

Abaixo encontra-se a representação da modelação orientada a objetos do projeto, ilustrando os relacionamentos de herança, composição e agregação:

```mermaid
classDiagram
    direction TB

    %% ==========================================
    %% CAMADA DE INTERFACE (FASTAPI)
    %% ==========================================
    class RotasAPI {
        <<Router - FastAPI>>
        +criar_midia(payload: MidiaSchemaCreate)
        +listar_midias()
        +obter_relatorios()
    }

    class MidiaSchemaCreate {
        <<Pydantic Schema>>
        +titulo: str
        +tipo: str
        +ano: int
        +duracao_minutos: int
    }

    %% ==========================================
    %% CAMADA DE PERSISTÊNCIA (SQLITE / ORM)
    %% ==========================================
    class MidiaRepository {
        <<Repository>>
        -db_session: Session
        +salvar(midia: Midia)
        +buscar_por_id(id: int) Midia
    }

    class ORMBase {
        <<SQLAlchemy / SQLModel Base>>
    }

    %% ==========================================
    %% ENUMS E EXCEÇÕES DE DOMÍNIO
    %% ==========================================
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

    class DominioError { <<exception>> }
    class ValorInvalidoError { <<exception>> }
    class EstadoInvalidoError { <<exception>> }

    DominioError <|-- ValorInvalidoError
    DominioError <|-- EstadoInvalidoError

    %% ==========================================
    %% MIXINS
    %% ==========================================
    class AvaliavelMixin {
        <<mixin>>
        -_nota: float | None
        +nota() float | None
        +avaliar(valor: float) void
    }

    class SerializavelMixin {
        <<mixin>>
        +to_dict() dict
    }

    %% ==========================================
    %% CAMADA DE DOMÍNIO (MAPEADA NO ORM)
    %% ==========================================
    class Midia {
        <<abstract / ORM Model>>
        -_titulo: String
        -_tipo: TipoMidia
        -_genero: String
        -_ano: int
        -classificacao_indicativa: String
        -_elenco: List~String~
        -_status: StatusVisualizacao
        -_data_conclusao: datetime | None
        +titulo() String
        +genero() String
        +ano() int
        +tipo() TipoMidia
        +elenco() List~String~
        +data_conclusao() datetime | None
        +status() StatusVisualizacao
        +duracao_minutos()* int
        +alterar_status(novo_status: StatusVisualizacao) void <<@registrar_evento>>
        +from_dict(dados: dict)$ Midia
        +converter_minutos_para_horas(minutos: int, multiplicador: float)$ float
        +__str__() String
        +__repr__() String
        +__eq__(outro: Object) bool
        +__lt__(outro: Object) bool
    }

    class Filme {
        <<ORM Model>>
        -_duracao_minutos: int
        +duracao_minutos() int
        +__str__() String
    }

    class Serie {
        <<ORM Model>>
        -temporadas: List~Temporada~
        +duracao_minutos() int
        +nota() float | None
        +atualizar_status() void
        +adicionar_temporada(temporada: Temporada) void
        +__len__() int
        +__str__() String
    }

    class Temporada {
        <<ORM Model>>
        -_numero: int
        -episodios: List~Episodio~
        +numero() int
        +duracao_minutos() int
        +adicionar_episodio(episodio: Episodio) void
        +calcular_nota_media() float | None
        +__len__() int
        +__repr__() String
        +__str__() String
    }

    class Episodio {
        <<ORM Model>>
        -_numero_temporada: int
        -_numero_episodio: int
        -_titulo: String
        -_duracao_minutos: int
        -_data_lancamento: date | None
        -_status: StatusVisualizacao
        +titulo() String
        +numero_temporada() int
        +numero_episodio() int
        +duracao_minutos() int
        +data_lancamento() date | None
        +status() StatusVisualizacao
        +alterar_status(novo_status: StatusVisualizacao) void <<@registrar_evento>>
        +__repr__() String
        +__str__() String
    }

    class Usuario {
        <<ORM Model>>
        -id_usuario: String
        -nome: String
        -email: String
        +criar_lista(nome: String) ListaPersonalizada
        +adicionar_favorito(midia: Midia) void
    }

    class ListaPersonalizada {
        <<ORM Model>>
        -nome: String
        +adicionar_midia(midia: Midia) void
        +remover_midia(midia: Midia) void
    }

    class RegistroHistorico {
        <<ORM Model>>
        -midia: Midia
        -data_hora: datetime
        +data_hora() datetime
    }

    %% ==========================================
    %% RELACIONAMENTOS DE HERANÇA E ORM
    %% ==========================================
    ORMBase <|-- Midia : Herda
    ORMBase <|-- Temporada : Herda
    ORMBase <|-- Episodio : Herda
    ORMBase <|-- Usuario : Herda
    ORMBase <|-- ListaPersonalizada : Herda
    ORMBase <|-- RegistroHistorico : Herda

    Midia <|-- Filme : Herança (Polimorfismo)
    Midia <|-- Serie : Herança (Polimorfismo)

    AvaliavelMixin <|-- Midia : Utiliza
    SerializavelMixin <|-- Midia : Utiliza
    AvaliavelMixin <|-- Episodio : Utiliza
    SerializavelMixin <|-- Episodio : Utiliza

    %% ==========================================
    %% RELACIONAMENTOS DE ASSOCIAÇÃO
    %% ==========================================
    Serie "1" o-- "*" Temporada : Agrega
    Temporada "1" *-- "*" Episodio : Contém (Composição)
    Usuario "1" *-- "*" ListaPersonalizada : gerencia
    Usuario "1" *-- "*" RegistroHistorico : registra
    ListaPersonalizada "*" o-- "*" Midia : agrupa
    RegistroHistorico --> Midia : refere-se

    %% Uso de Enums
    Midia --> TipoMidia : possui
    Midia --> StatusVisualizacao : possui
    Episodio --> StatusVisualizacao : possui

    %% ==========================================
    %% FLUXO DOS FRAMEWORKS EXTERNOS
    %% ==========================================
    RotasAPI ..> MidiaSchemaCreate : Valida JSON
    RotasAPI --> MidiaRepository : Solicita Operações
    MidiaRepository --> Midia : Persiste no SQLite


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
