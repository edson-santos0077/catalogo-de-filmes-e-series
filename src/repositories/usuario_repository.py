import json
import os
from abc import ABC, abstractmethod

from src.models.usuario import Usuario
from src.repositories.database import (
    JSON_USUARIOS_PATH,
    inicializar_banco,
    obter_conexao,
)


def _converter_para_json_dict(obj):
    """Converte objetos complexos e listas (como ListaPersonalizada) recursivamente para dict."""
    if hasattr(obj, "to_dict") and callable(obj.to_dict):
        return _converter_para_json_dict(obj.to_dict())
    if isinstance(obj, dict):
        return {k: _converter_para_json_dict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_converter_para_json_dict(i) for i in obj]
    if hasattr(obj, "__dict__"):
        return {k: _converter_para_json_dict(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
    return obj


class UsuarioRepository(ABC):
    """Interface abstrata para o repositório de usuários."""

    @abstractmethod
    def salvar(self, usuario: Usuario) -> None:
        pass

    @abstractmethod
    def obter_por_id(self, id_usuario: str | int) -> Usuario | None:
        pass

    @abstractmethod
    def obter_por_email(self, email: str) -> Usuario | None:
        pass

    @abstractmethod
    def adicionar(self, usuario: Usuario) -> Usuario:
        pass

    @abstractmethod
    def atualizar(self, usuario: Usuario) -> None:
        pass

    @abstractmethod
    def listar_todos(self) -> list[Usuario]:
        pass


class UsuarioRepositoryJSON(UsuarioRepository):
    """Repositório de usuários persistindo em arquivo JSON."""

    def __init__(self, caminho: str = JSON_USUARIOS_PATH):
        self.caminho = caminho
        os.makedirs(os.path.dirname(self.caminho), exist_ok=True)

    def _carregar_todos_dict(self) -> dict:
        if not os.path.exists(self.caminho):
            return {}
        with open(self.caminho, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def salvar(self, usuario: Usuario) -> None:
        dados_usuarios = self._carregar_todos_dict()
        key = str(usuario.id_usuario)

        dados_brutos = usuario.to_dict() if hasattr(usuario, "to_dict") else usuario.__dict__
        dados_usuarios[key] = _converter_para_json_dict(dados_brutos)

        with open(self.caminho, "w", encoding="utf-8") as f:
            json.dump(dados_usuarios, f, indent=4, ensure_ascii=False)

    def obter_por_id(self, id_usuario: str | int) -> Usuario | None:
        dados_usuarios = self._carregar_todos_dict()
        dados = dados_usuarios.get(str(id_usuario))
        if not dados:
            return None

        return Usuario.from_dict(dados)

    def listar_todos(self) -> list[Usuario]:
        dados_usuarios = self._carregar_todos_dict()
        return [Usuario.from_dict(dados) for dados in dados_usuarios.values()]

    def obter_por_email(self, email: str) -> Usuario | None:
        for usuario in self.listar_todos():
            if usuario.email == email:
                return usuario
        return None

    def adicionar(self, usuario: Usuario) -> Usuario:
        self.salvar(usuario)
        return usuario

    def atualizar(self, usuario: Usuario) -> None:
        self.salvar(usuario)


class UsuarioRepositorySQLite(UsuarioRepository):
    """Repositório de usuários persistindo em SQLite."""

    def __init__(self):
        inicializar_banco()

    def salvar(self, usuario: Usuario) -> None:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                """
                INSERT INTO usuarios (id_usuario, nome, email, limite_listas)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id_usuario) DO UPDATE SET
                    nome=excluded.nome,
                    email=excluded.email,
                    limite_listas=excluded.limite_listas
                """,
                (
                    str(usuario.id_usuario),
                    usuario.nome,
                    usuario.email,
                    usuario.limite_listas,
                ),
            )

    def obter_por_id(self, id_usuario: str | int) -> Usuario | None:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT * FROM usuarios WHERE id_usuario = ?", (str(id_usuario),)
            )
            linha = cursor.fetchone()
            if not linha:
                return None
            dados = dict(linha)
            return Usuario(
                id_usuario=dados["id_usuario"],
                nome=dados["nome"],
                email=dados["email"],
                limite_listas=dados["limite_listas"],
            )

    def listar_todos(self) -> list[Usuario]:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM usuarios")
            linhas = cursor.fetchall()

            return [
                Usuario(
                    id_usuario=linha["id_usuario"],
                    nome=linha["nome"],
                    email=linha["email"],
                    limite_listas=linha["limite_listas"],
                )
                for linha in linhas
            ]

    def obter_por_email(self, email: str) -> Usuario | None:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
            linha = cursor.fetchone()
            if not linha:
                return None

            dados = dict(linha)
            return Usuario(
                id_usuario=dados["id_usuario"],
                nome=dados["nome"],
                email=dados["email"],
                limite_listas=dados["limite_listas"],
            )

    def adicionar(self, usuario: Usuario) -> Usuario:
        self.salvar(usuario)
        return usuario

    def atualizar(self, usuario: Usuario) -> None:
        self.salvar(usuario)


class UsuarioRepositorySincronizado(UsuarioRepository):
    """Repositório híbrido que sincroniza usuários no SQLite e JSON simultaneamente."""

    def __init__(self):
        self.sqlite_repo = UsuarioRepositorySQLite()
        self.json_repo = UsuarioRepositoryJSON()

    def salvar(self, usuario: Usuario) -> None:
        self.sqlite_repo.salvar(usuario)
        self.json_repo.salvar(usuario)

    def obter_por_id(self, id_usuario: str | int) -> Usuario | None:
        try:
            u = self.sqlite_repo.obter_por_id(id_usuario)
            if u:
                return u
        except Exception:
            pass
        return self.json_repo.obter_por_id(id_usuario)

    def obter_por_email(self, email: str) -> Usuario | None:
        try:
            u = self.sqlite_repo.obter_por_email(email)
            if u:
                return u
        except Exception:
            pass
        return self.json_repo.obter_por_email(email)

    def listar_todos(self) -> list[Usuario]:
        try:
            usuarios = self.sqlite_repo.listar_todos()
            if usuarios:
                return usuarios
        except Exception:
            pass
        return self.json_repo.listar_todos()

    def adicionar(self, usuario: Usuario) -> Usuario:
        res = self.sqlite_repo.adicionar(usuario)
        self.json_repo.adicionar(usuario)
        return res

    def atualizar(self, usuario: Usuario) -> None:
        self.sqlite_repo.atualizar(usuario)
        self.json_repo.atualizar(usuario)


def get_usuario_repository() -> UsuarioRepository:
    """Retorna o repositório de usuários ativo com suporte a modo SINCRONIZADO, SQLITE ou JSON."""
    try:
        from src.core.configuracao import configuracao_global
        backend_config = getattr(configuracao_global, "backend_persistencia", "SINCRONIZADO")
    except Exception:
        backend_config = "SINCRONIZADO"

    tipo_banco = os.getenv("TIPO_BANCO", backend_config).upper()

    if tipo_banco == "JSON":
        return UsuarioRepositoryJSON()
    if tipo_banco == "SQLITE":
        return UsuarioRepositorySQLite()

    return UsuarioRepositorySincronizado()
