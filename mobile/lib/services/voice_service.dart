import 'dart:async';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;

class VoiceService {
  final FlutterTts _tts = FlutterTts();
  final stt.SpeechToText _stt = stt.SpeechToText();
  
  bool _isTtsInitialized = false;
  bool _isSttInitialized = false;

  /// Inicializa los motores de voz.
  Future<void> init() async {
    // Configurar TTS
    await _tts.setLanguage("es-ES"); // Español
    await _tts.setPitch(1.1); // Tono ligeramente más agudo para sonar amigable
    await _tts.setSpeechRate(0.5); // Velocidad normal
    
    // Opcional: Intentar usar una voz específica si está disponible
    // final voices = await _tts.getVoices;
    // (Aquí podríamos filtrar para elegir la mejor voz local, 
    // pero por defecto usará la mejor disponible en español)
    
    await _tts.awaitSpeakCompletion(true);
    
    _tts.setCompletionHandler(() {
      if (_onTtsCompleteCallback != null) {
        _onTtsCompleteCallback!();
      }
    });

    _isTtsInitialized = true;

    // Configurar STT
    _isSttInitialized = await _stt.initialize(
      onStatus: (status) {
        if (_onStatusCallback != null) {
          _onStatusCallback!(status);
        }
      }
    );
  }

  Function(String)? _onStatusCallback;
  Function()? _onTtsCompleteCallback;

  void setOnStatusCallback(Function(String)? callback) {
    _onStatusCallback = callback;
  }

  void setOnTtsCompleteCallback(Function()? callback) {
    _onTtsCompleteCallback = callback;
  }

  /// Empieza a escuchar la voz del usuario.
  Future<void> startListening(Function(String) onResult) async {
    if (!_isSttInitialized) {
      await init();
    }
    if (_isSttInitialized && !_stt.isListening) {
      await _stt.listen(
        onResult: (result) {
          onResult(result.recognizedWords);
        },
        listenOptions: stt.SpeechListenOptions(
          partialResults: true,
          cancelOnError: true,
        ),
      );
    }
  }

  /// Deja de escuchar.
  Future<void> stopListening() async {
    if (_stt.isListening) {
      await _stt.stop();
    }
  }

  bool get isListening => _stt.isListening;

  final List<String> _ttsQueue = [];
  bool _isSpeaking = false;

  /// Reproduce texto en voz alta usando un sistema de cola
  /// para evitar que una nueva oración corte a la anterior.
  Future<void> speak(String text) async {
    if (!_isTtsInitialized) {
      await init();
    }
    if (text.isNotEmpty) {
      _ttsQueue.add(text);
      _processQueue();
    }
  }

  Future<void> _processQueue() async {
    if (_isSpeaking || _ttsQueue.isEmpty) return;
    _isSpeaking = true;
    
    while (_ttsQueue.isNotEmpty) {
      String nextText = _ttsQueue.removeAt(0);
      await _tts.speak(nextText);
      // Gracias a awaitSpeakCompletion(true), esto espera a que termine de hablar
    }
    
    _isSpeaking = false;
  }

  /// Detiene la reproducción de voz y vacía la cola.
  Future<void> stopSpeaking() async {
    _ttsQueue.clear();
    _isSpeaking = false;
    await _tts.stop();
  }

  void dispose() {
    _ttsQueue.clear();
    _tts.stop();
    _stt.stop();
  }
}
