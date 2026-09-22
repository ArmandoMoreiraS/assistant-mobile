import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';

import '../providers/chat_provider.dart';
import '../config/theme.dart';

class CallScreen extends ConsumerStatefulWidget {
  const CallScreen({super.key});

  @override
  ConsumerState<CallScreen> createState() => _CallScreenState();
}

class _CallScreenState extends ConsumerState<CallScreen>
    with SingleTickerProviderStateMixin {
  String _currentText = '';
  bool _isAgentSpeaking = false;
  late AnimationController _animController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat(reverse: true);
    
    _pulseAnimation = Tween<double>(begin: 0.8, end: 1.2).animate(
      CurvedAnimation(parent: _animController, curve: Curves.easeInOut),
    );

    WidgetsBinding.instance.addPostFrameCallback((_) {
      _setupVoiceCallbacks();
      _startListening();
    });
  }

  void _setupVoiceCallbacks() {
    final voiceService = ref.read(voiceServiceProvider);
    
    voiceService.setOnStatusCallback((status) {
      if (status == 'done' || status == 'notListening') {
        if (_currentText.trim().isNotEmpty && mounted && !_isAgentSpeaking) {
           _sendMessage(_currentText);
           _currentText = '';
        }
      }
    });

    voiceService.setOnTtsCompleteCallback(() {
      if (mounted) {
        setState(() {
          _isAgentSpeaking = false;
        });
        // Reiniciar escucha automáticamente tras hablar
        _startListening();
      }
    });
  }

  void _startListening() {
    if (mounted && !_isAgentSpeaking) {
       ref.read(chatProvider.notifier).startListening((text) {
         if (mounted) {
           setState(() {
             _currentText = text;
           });
         }
       });
    }
  }

  void _sendMessage(String text) async {
    final notifier = ref.read(chatProvider.notifier);
    await notifier.stopListening();
    setState(() {
       _isAgentSpeaking = true;
    });
    await notifier.sendMessage(text);
  }

  @override
  void dispose() {
    _animController.dispose();
    // Restaurar el estado natural al salir
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final voiceService = ref.read(voiceServiceProvider);
      voiceService.setOnStatusCallback(null);
      voiceService.setOnTtsCompleteCallback(null);
      voiceService.stopListening();
      voiceService.stopSpeaking();
    });
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatProvider);
    final isThinking = chatState.isLoading;
    final isListening = chatState.isListening;

    Color stateColor;
    String stateText;

    // TEMA 21 DE SEPTIEMBRE (Flores Amarillas)
    if (isThinking) {
      stateColor = Colors.amber.shade300;
      stateText = "Pensando en flores... 🌼";
    } else if (_isAgentSpeaking) {
      stateColor = Colors.yellowAccent;
      stateText = "Hablando... 🌻";
    } else if (isListening) {
      stateColor = Colors.amber;
      stateText = "Te escucho... 🌻";
    } else {
      stateColor = Colors.amber.shade200;
      stateText = "Esperando... 🌼";
    }

    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      body: SafeArea(
        child: Column(
          children: [
            // Header
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.keyboard_arrow_down, size: 32),
                    color: Colors.white,
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
            ),
            
            Expanded(
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    ScaleTransition(
                      scale: _pulseAnimation,
                      child: Container(
                        width: 150,
                        height: 150,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: stateColor.withValues(alpha: 0.2),
                          border: Border.all(color: stateColor, width: 2),
                        ),
                        child: Center(
                          child: Icon(
                            isThinking 
                              ? Icons.filter_vintage // Flor vintage
                              : (isListening ? Icons.mic : Icons.local_florist), // Flor
                            size: 64,
                            color: stateColor,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 40),
                    Text(
                      stateText,
                      style: GoogleFonts.inter(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 20),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 32.0),
                      child: Text(
                        _currentText,
                        textAlign: TextAlign.center,
                        style: GoogleFonts.inter(
                          color: AppTheme.textSecondary,
                          fontSize: 16,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            // Botón de Colgar
            Padding(
              padding: const EdgeInsets.only(bottom: 40.0),
              child: InkWell(
                onTap: () => Navigator.pop(context),
                borderRadius: BorderRadius.circular(32),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                  decoration: BoxDecoration(
                    color: Colors.redAccent.withValues(alpha: 0.8),
                    borderRadius: BorderRadius.circular(32),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.call_end, color: Colors.white),
                      const SizedBox(width: 12),
                      Text(
                        'Terminar Llamada',
                        style: GoogleFonts.inter(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
