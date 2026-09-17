"""Módulo de sesión del AI Companion — orquesta memoria, prompts y LLM."""

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from ai_foundation.llm import get_llm
from ai_foundation.utils.logging import logger

from .extractor import extract_info, update_profile_from_extraction
from .memory import load_history, load_profile, save_history, save_profile
from .models import Turn
from .prompts import build_system_prompt

MAX_HISTORY_TURNS = 20


class CompanionSession:
    def __init__(self, user_id: str, llm: BaseChatModel | None = None):
        self.user_id = user_id
        self.profile = load_profile(user_id)
        self.history: list[Turn] = load_history(user_id)
        self.llm = llm or get_llm()

    def chat(self, user_input: str) -> str:
        """Envía un mensaje y retorna la respuesta del Companion."""
        self.history.append(Turn(role="user", content=user_input))

        # Construir mensajes para el LLM
        system_prompt = build_system_prompt(self.profile)
        messages = [SystemMessage(content=system_prompt)]

        # Agregar historial (máximo MAX_HISTORY_TURNS turnos)
        for turn in self.history[-MAX_HISTORY_TURNS:]:
            if turn.role == "user":
                messages.append(HumanMessage(content=turn.content))
            elif turn.role == "assistant":
                messages.append(AIMessage(content=turn.content))

        try:
            response = self.llm.invoke(messages)
            # Gemini devuelve content como lista o string
            if isinstance(response.content, list):
                assistant_content = next(
                    (item["text"] for item in response.content if item.get("type") == "text"),
                    str(response.content),
                )
            else:
                assistant_content = str(response.content)
        except Exception as e:
            logger.error(f"Error al invocar LLM: {e}")
            assistant_content = "Lo siento, tuve un problema al procesar tu mensaje. ¿Puedes intentarlo de nuevo?"

        self.history.append(Turn(role="assistant", content=assistant_content))

        # Mantener ventana deslizante
        # NOTA: si queremos persistir TODA la conversación, tal vez no deberíamos truncar history.
        # Pero para memoria del LLM está bien, el historial completo se podría guardar aparte.
        # De momento mantendremos todo el historial en persistencia, truncando solo para el LLM.
        # Cambiaremos el truncamiento para pasarlo solo a los mensajes de LangChain, y en history guardamos todo.
        
        save_history(self.user_id, self.history)
        return assistant_content

    def end_session(self) -> None:
        """Extrae información del usuario y guarda el perfil actualizado."""
        try:
            extracted = extract_info(self.history)
            self.profile = update_profile_from_extraction(self.profile, extracted)
        except Exception as e:
            logger.error(f"Error en extracción de información: {e}")

        save_profile(self.user_id, self.profile)
        logger.info(f"Sesión finalizada y perfil guardado para usuario '{self.user_id}'.")
