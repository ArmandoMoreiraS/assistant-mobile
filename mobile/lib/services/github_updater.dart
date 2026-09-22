import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:package_info_plus/package_info_plus.dart';
import 'package:url_launcher/url_launcher.dart';

class GithubUpdater {
  static const String repoOwner = 'ArmandoMoreiraS';
  static const String repoName = 'assistant-mobile';
  
  /// Revisa en GitHub si hay una versión más reciente.
  /// Si la hay, muestra un diálogo preguntando si desea instalarla.
  static Future<void> checkForUpdates(BuildContext context) async {
    try {
      // 1. Obtener la versión local de la app
      final PackageInfo packageInfo = await PackageInfo.fromPlatform();
      final String currentVersionStr = '${packageInfo.version}+${packageInfo.buildNumber}';
      
      // 2. Consultar el último Release en GitHub
      final response = await http.get(Uri.parse(
          'https://api.github.com/repos/$repoOwner/$repoName/releases/latest'));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final String latestTag = data['tag_name']; // ej. "v1.0.0+2"
        
        // Limpiamos la 'v' si la tiene
        final String latestVersionStr = latestTag.replaceAll('v', '');
        
        // 3. Comparar (lógica simple de strings, idealmente se usa librería semver)
        if (currentVersionStr != latestVersionStr) {
          // Hay una nueva versión
          final String? downloadUrl = _getApkUrl(data['assets']);
          if (downloadUrl != null && context.mounted) {
            _showUpdateDialog(context, latestVersionStr, downloadUrl);
          }
        }
      }
    } catch (e) {
      debugPrint('Error comprobando actualizaciones: $e');
    }
  }

  static String? _getApkUrl(List<dynamic> assets) {
    for (var asset in assets) {
      if (asset['name'].toString().endsWith('.apk')) {
        return asset['browser_download_url'];
      }
    }
    return null;
  }

  static void _showUpdateDialog(BuildContext context, String newVersion, String url) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('🌸 ¡Nueva Actualización!'),
        content: Text('Hay una nueva versión del Companion disponible (v$newVersion).\n\n¿Deseas descargarla e instalarla ahora?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Más tarde', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context);
              final Uri uri = Uri.parse(url);
              if (await canLaunchUrl(uri)) {
                // Al lanzarlo, Android descargará el APK y preguntará para instalarlo
                await launchUrl(uri, mode: LaunchMode.externalApplication);
              }
            },
            child: const Text('Actualizar'),
          ),
        ],
      ),
    );
  }
}
