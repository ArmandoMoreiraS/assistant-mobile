import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'config/theme.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const ProviderScope(child: AiCompanionApp()));
}

class AiCompanionApp extends StatelessWidget {
  const AiCompanionApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Companion',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const HomeScreen(),
    );
  }
}
