import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/api_config.dart';
import '../models/profile.dart';

/// Servicio para obtener perfiles de usuario desde la API.
class ProfileService {
  final http.Client _client = http.Client();

  /// Obtiene el perfil de un usuario.
  Future<UserProfileModel> getProfile(String userId) async {
    final uri =
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.profileEndpoint}/$userId');
    final response = await _client.get(uri);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return UserProfileModel.fromJson(data);
    } else {
      throw Exception('Error al obtener perfil: ${response.statusCode}');
    }
  }

  void dispose() {
    _client.close();
  }
}
