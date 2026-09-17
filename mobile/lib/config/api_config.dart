/// Configuración de la API del backend.
class ApiConfig {
  /// URL base del servidor FastAPI.
  /// Para emulador Android usa 10.0.2.2 (alias del localhost del host).
  /// Para dispositivo físico, usa la IP de tu máquina en la red local.
  static const String baseUrl = 'http://10.0.2.2:8000';

  /// ID fijo del único usuario de la app.
  static const String userId = 'mi_persona';

  static const String chatEndpoint = '/api/v1/chat';
  static const String chatStreamEndpoint = '/api/v1/chat/stream';
  static const String profileEndpoint = '/api/v1/profile';
  static const String endSessionEndpoint = '/api/v1/session/end';
  static const String healthEndpoint = '/api/v1/health';
}
