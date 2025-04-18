"""
Contêiner para injeção de dependências.
Centraliza a criação e gerenciamento de dependências do sistema.
"""

import logging

logger = logging.getLogger(__name__)


class Container:
    """
    Contêiner para injeção de dependências.
    Permite registrar e obter instâncias de dependências.
    """

    _instances = {}

    @classmethod
    def register(cls, key: str, instance) -> None:
        """
        Registra uma instância de dependência.

        Args:
            key: Chave para identificar a dependência
            instance: Instância da dependência
        """
        cls._instances[key] = instance
        logger.debug(f"Dependência registrada: {key}")

    @classmethod
    def get(cls, key: str):
        """
        Obtém uma instância de dependência.

        Args:
            key: Chave da dependência

        Returns:
            Instância da dependência

        Raises:
            KeyError: Se a dependência não estiver registrada
        """
        if key not in cls._instances:
            logger.error(f"Dependência não encontrada: {key}")
            raise KeyError(f"Dependência não registrada: {key}")

        return cls._instances[key]

    @classmethod
    def has(cls, key: str) -> bool:
        """
        Verifica se uma dependência está registrada.

        Args:
            key: Chave da dependência

        Returns:
            bool: True se a dependência estiver registrada
        """
        return key in cls._instances

    @classmethod
    def clear(cls) -> None:
        """Limpa todas as dependências registradas."""
        cls._instances.clear()
        logger.debug("Todas as dependências foram limpas")