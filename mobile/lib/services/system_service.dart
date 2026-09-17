import 'package:flutter/services.dart';

class SystemService {
  static const platform = MethodChannel('com.example.ai_companion/screen_context');

  /// Obtiene el contexto actual de la pantalla usando el AccessibilityService de Android.
  static Future<String> getScreenContext() async {
    try {
      final String contextText = await platform.invokeMethod('getScreenContext');
      return contextText.trim();
    } on PlatformException catch (_) {
      return '';
    }
  }
}
