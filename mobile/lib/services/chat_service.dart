import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/api_config.dart';

/// Servicio de chat que se comunica con la API FastAPI.
class ChatService {
  final http.Client _client = http.Client();

  /// Envía un mensaje y recibe la respuesta completa (sin streaming).
  Future<String> sendMessage(String userId, String message) async {
    final uri = Uri.parse('${ApiConfig.baseUrl}${ApiConfig.chatEndpoint}');
    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'user_id': userId, 'message': message}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['response'] as String;
    } else {
      throw Exception('Error en chat: ${response.statusCode}');
    }
  }

  /// Envía un mensaje y recibe tokens como SSE streaming.
  Stream<String> streamMessage(String userId, String message) async* {
    final uri =
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.chatStreamEndpoint}');
    final request = http.Request('POST', uri);
    request.headers['Content-Type'] = 'application/json';
    request.body = jsonEncode({'user_id': userId, 'message': message});

    final streamedResponse = await _client.send(request);

    if (streamedResponse.statusCode != 200) {
      throw Exception('Error en streaming: ${streamedResponse.statusCode}');
    }

    // Buffer para manejar chunks parciales
    String buffer = '';

    await for (final chunk
        in streamedResponse.stream.transform(utf8.decoder)) {
      buffer += chunk;

      // Procesar líneas completas del buffer
      while (buffer.contains('\n')) {
        final newlineIndex = buffer.indexOf('\n');
        final line = buffer.substring(0, newlineIndex).trim();
        buffer = buffer.substring(newlineIndex + 1);

        if (line.startsWith('data: ')) {
          final data = line.substring(6);
          try {
            final parsed = jsonDecode(data);
            if (parsed['type'] == 'done') {
              return;
            } else if (parsed['type'] == 'error') {
              yield '[ERROR] ${parsed['content']}';
            } else if (parsed['type'] == 'token') {
              yield parsed['content'] as String;
            }
          } catch (_) {
            // Ignorar JSON malformado
          }
        }
      }
    }
  }

  /// Finaliza la sesión del usuario.
  Future<void> endSession(String userId) async {
    final uri =
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.endSessionEndpoint}');
    await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'user_id': userId}),
    );
  }

  /// Health check del servidor.
  Future<bool> isServerHealthy() async {
    try {
      final uri =
          Uri.parse('${ApiConfig.baseUrl}${ApiConfig.healthEndpoint}');
      final response = await _client.get(uri).timeout(
        const Duration(seconds: 3),
      );
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  /// Obtiene el historial de chat persistente.
  Future<List<Map<String, dynamic>>> getHistory(String userId) async {
    final uri = Uri.parse('${ApiConfig.baseUrl}/api/v1/chat/history/$userId');
    try {
      final response = await _client.get(uri);
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final history = data['history'] as List;
        return history.map((e) => e as Map<String, dynamic>).toList();
      }
    } catch (_) {}
    return [];
  }

  void dispose() {
    _client.close();
  }
}
