import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';
import '../config/api_config.dart';

class CommandService {
  /// Busca comandos en el texto, los ejecuta y devuelve el texto limpio.
  static Future<String> processCommands(String text) async {
    final regex = RegExp(r'\[CMD:(.*?)\]');
    final matches = regex.allMatches(text);

    for (final match in matches) {
      final commandContent = match.group(1);
      if (commandContent != null) {
        await _executeCommand(commandContent);
      }
    }

    // Retorna el texto sin los comandos
    return text.replaceAll(regex, '').trim();
  }

  static Future<void> _executeCommand(String commandContent) async {
    final parts = commandContent.split(':');
    if (parts.isEmpty) return;

    final action = parts[0].toUpperCase();

    try {
      switch (action) {
        case 'YOUTUBE':
          if (parts.length > 1) {
            final query = parts.sublist(1).join(':').trim();
            final url = Uri.parse('https://www.youtube.com/results?search_query=${Uri.encodeComponent(query)}');
            await launchUrl(url, mode: LaunchMode.externalApplication);
          }
          break;
        case 'CALL':
          if (parts.length > 1) {
            final number = parts[1].trim();
            final url = Uri.parse('tel:$number');
            await launchUrl(url);
          }
          break;
        case 'WHATSAPP':
          if (parts.length > 1) {
            final number = parts[1].trim();
            final message = parts.length > 2 ? parts.sublist(2).join(':').trim() : '';
            final url = Uri.parse('https://wa.me/$number?text=${Uri.encodeComponent(message)}');
            await launchUrl(url, mode: LaunchMode.externalApplication);
          }
          break;
        case 'WEB':
          if (parts.length > 1) {
            final urlString = parts.sublist(1).join(':').trim();
            final url = Uri.parse(urlString);
            await launchUrl(url, mode: LaunchMode.externalApplication);
          }
          break;
        case 'ARTEMIS':
          if (parts.length > 1) {
            final task = parts.sublist(1).join(':').trim();
            // Llama a la API del backend para ejecutar Artemis
            final uri = Uri.parse('${ApiConfig.baseUrl}/api/v1/artemis/run');
            final request = http.Request('POST', uri);
            request.headers['Content-Type'] = 'application/json';
            request.body = '{"task": "$task"}';
            // Lo enviamos y no esperamos para no bloquear
            http.Client().send(request);
          }
          break;
      }
    } catch (e) {
      // Ignorar errores de lanzamiento de URL en producción
    }
  }
}
