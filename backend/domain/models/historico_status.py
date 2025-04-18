# Implementar tabela e repositório para histórico

# backend/domain/models/historico_status.py
@dataclass
class HistoricoStatus:
    """
    Representa uma mudança de status de um pedido.
    """
    id: Optional[int]
    pedido_id: int
    status_anterior: str
    status_novo: str
    usuario_id: int
    observacoes: Optional[str]
    data_alteracao: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "pedido_id": self.pedido_id,
            "status_anterior": self.status_anterior,
            "status_novo": self.status_novo,
            "usuario_id": self.usuario_id,
            "observacoes": self.observacoes,
            "data_alteracao": self.data_alteracao.isoformat()
        }


# backend/infrastructure/repositories/historico_repository.py
class HistoricoRepository:
    """
    Repositório para histórico de alterações de status de pedidos.
    """

    def registrar_alteracao(self, historico: HistoricoStatus) -> HistoricoStatus:
        """
        Registra uma alteração de status no histórico.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Inserir registro
            cursor.execute("""
                INSERT INTO historico_status (
                    pedido_id, status_anterior, status_novo, 
                    usuario_id, observacoes, data_alteracao
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                historico.pedido_id,
                historico.status_anterior,
                historico.status_novo,
                historico.usuario_id,
                historico.observacoes,
                historico.data_alteracao
            ))

            # Obter ID
            historico.id = cursor.lastrowid

            conn.commit()
            return historico

        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao registrar alteração de status: {str(e)}")
            raise

        finally:
            cursor.close()
            conn.close()