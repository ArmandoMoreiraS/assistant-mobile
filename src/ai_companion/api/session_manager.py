"""Gestión de sesiones activas del AI Companion."""

from ai_companion.session import CompanionSession


class SessionManager:
    """Mantiene las sesiones activas en memoria del servidor."""

    def __init__(self):
        self._sessions: dict[str, CompanionSession] = {}

    def get_or_create(self, user_id: str) -> CompanionSession:
        """Obtiene una sesión existente o crea una nueva."""
        if user_id not in self._sessions:
            self._sessions[user_id] = CompanionSession(user_id=user_id)
        return self._sessions[user_id]

    def end_session(self, user_id: str) -> None:
        """Finaliza una sesión: extrae info, guarda perfil y la elimina de memoria."""
        if user_id in self._sessions:
            self._sessions[user_id].end_session()
            del self._sessions[user_id]

    def has_session(self, user_id: str) -> bool:
        return user_id in self._sessions


# Singleton global
session_manager = SessionManager()
