import json
import os
from abc import ABC, abstractmethod

from src.models.usuario import Usuario
from src.repositories.database import JSON_USUARIOS_PATH, inicializar_banco, obter_conexao


class UsuarioRepository(ABC):
    """Interface abstrata para o repositório de usuários."""

    @abstractmethod
    def salvar(self, usuario: Usuario) -> None:
        pass

    @abstractmethod
    def obter_por_id(self, id_usuario: str | int) -> Usuario | None:
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
        dados_usuarios[key] = usuario.to_dict()

        with open(self.caminho, "w", encoding="utf-8") as f:
            json.dump(dados_usuarios, f, indent=4, ensure_ascii=False)

    def obter_por_id(self, id_usuario: str | int) -> Usuario | None:
        dados_usuarios = self._carregar_todos_dict()
        dados = dados_usuarios.get(str(id_usuario))
        if not dados:
            return None

        return Usuario.from_dict(dados)


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
