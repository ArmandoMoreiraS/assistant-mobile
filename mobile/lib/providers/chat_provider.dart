import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/message.dart';
import '../services/chat_service.dart';
import '../services/command_service.dart';
import '../services/system_service.dart';
import '../services/voice_service.dart';

/// Provider global del VoiceService.
final voiceServiceProvider = Provider<VoiceService>((ref) {
  final service = VoiceService();
  return service;
});

/// Provider global del ChatService.
final chatServiceProvider = Provider<ChatService>((ref) {
  final service = ChatService();
  ref.onDispose(() => service.dispose());
  return service;
});

/// Estado del chat.
class ChatState {
  final List<ChatMessage> messages;
  final bool isLoading;
  final bool isListening; // Nuevo estado para UI del micrófono
  final String? error;

  const ChatState({
    this.messages = const [],
    this.isLoading = false,
    this.isListening = false,
    this.error,
  });

  ChatState copyWith({
    List<ChatMessage>? messages,
    bool? isLoading,
    bool? isListening,
    String? error,
  }) {
    return ChatState(
      messages: messages ?? this.messages,
      isLoading: isLoading ?? this.isLoading,
      isListening: isListening ?? this.isListening,
      error: error,
    );
  }
}

/// Notifier del chat — gestiona el estado de la conversación.
class ChatNotifier extends Notifier<ChatState> {
  late final ChatService _chatService;
  late final VoiceService _voiceService;
  late final String _userId;

  @override
  ChatState build() {
    _chatService = ref.read(chatServiceProvider);
    _voiceService = ref.read(voiceServiceProvider);
    // Asegurarnos que la voz se inicializa
    _voiceService.init();
    return const ChatState();
  }

  void setUserId(String userId) {
    _userId = userId;
    _loadInitialHistory();
  }

  Future<void> _loadInitialHistory() async {
    state = state.copyWith(isLoading: true);
    try {
      final historyRaw = await _chatService.getHistory(_userId);
      final messages = historyRaw.map((e) => ChatMessage(
        role: e['role'] as String,
        content: e['content'] as String,
      )).toList();
      state = state.copyWith(messages: messages, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  /// Envía un mensaje con streaming SSE.
  Future<void> sendMessage(String message) async {
    // Agregar mensaje del usuario (UI)
    final userMessage = ChatMessage(role: 'user', content: message);
    final updatedMessages = [...state.messages, userMessage];

    // Obtener contexto de pantalla
    String enrichedMessage = message;
    final screenContext = await SystemService.getScreenContext();
    if (screenContext.isNotEmpty) {
      // Limitamos el tamaño por si es muy largo
      final contextSub = screenContext.length > 2000 ? screenContext.substring(0, 2000) : screenContext;
      enrichedMessage = '$message\n\n[CONTEXTO VISUAL DEL SISTEMA (Lo que el usuario tiene en pantalla ahora mismo):\n$contextSub]';
    }

    // Agregar placeholder para la respuesta del companion
    final companionMessage = ChatMessage(
      role: 'assistant',
      content: '',
      isStreaming: true,
    );
    state = state.copyWith(
      messages: [...updatedMessages, companionMessage],
      isLoading: true,
      error: null,
    );

    try {
      String fullResponse = '';
      String currentSentence = '';

      await for (final token
          in _chatService.streamMessage(_userId, enrichedMessage)) {
        fullResponse += token;
        currentSentence += token;

        // Hablar porciones de oraciones a medida que llegan
        final match = RegExp(r'([.!?\n]+)(\s|$)').firstMatch(currentSentence);
        if (match != null) {
          String sentence = currentSentence.substring(0, match.end).trim();
          // Limpiar comandos para que no los lea el TTS
          sentence = sentence.replaceAll(RegExp(r'\[CMD:.*?\]?'), '').trim();
          if (sentence.isNotEmpty) {
            _voiceService.speak(sentence);
          }
          currentSentence = currentSentence.substring(match.end);
        }

        // Limpiar para la UI en tiempo real
        final displayResponse = fullResponse.replaceAll(RegExp(r'\[CMD:.*?\]?'), '').trim();

        // Actualizar el último mensaje con el contenido acumulado
        final msgs = List<ChatMessage>.from(state.messages);
        msgs[msgs.length - 1] = companionMessage.copyWith(
          content: displayResponse,
          isStreaming: true,
        );
        state = state.copyWith(messages: msgs);
      }

      // Hablar cualquier remanente al final
      String finalSentence = currentSentence.trim().replaceAll(RegExp(r'\[CMD:.*?\]?'), '').trim();
      if (finalSentence.isNotEmpty) {
        _voiceService.speak(finalSentence);
      }

      // Procesar comandos reales (abre apps) y limpiar el texto final
      final finalCleanResponse = await CommandService.processCommands(fullResponse);

      // Marcar como completado
      final msgs = List<ChatMessage>.from(state.messages);
      msgs[msgs.length - 1] = companionMessage.copyWith(
        content: finalCleanResponse,
        isStreaming: false,
      );
      state = state.copyWith(messages: msgs, isLoading: false);
    } catch (e) {
      // En caso de error, actualizar el mensaje con un fallback
      final msgs = List<ChatMessage>.from(state.messages);
      msgs[msgs.length - 1] = companionMessage.copyWith(
        content: 'Error de conexión. ¿El servidor está activo?',
        isStreaming: false,
      );
      state = state.copyWith(
        messages: msgs,
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Finaliza la sesión.
  Future<void> endSession() async {
    try {
      _voiceService.dispose();
      await _chatService.endSession(_userId);
    } catch (_) {
      // Silenciar errores al cerrar sesión
    }
  }

  /// Inicia el micrófono para escuchar al usuario.
  Future<void> startListening(Function(String) onRecognized) async {
    state = state.copyWith(isListening: true);
    await _voiceService.startListening((text) {
      onRecognized(text);
    });
  }

  /// Detiene el micrófono.
  Future<void> stopListening() async {
    await _voiceService.stopListening();
    state = state.copyWith(isListening: false);
  }

  /// Detiene la voz del agente.
  void stopSpeaking() {
    _voiceService.stopSpeaking();
  }
}

/// Provider del chat — uno por cada userId.
final chatProvider = NotifierProvider<ChatNotifier, ChatState>(
  ChatNotifier.new,
);
