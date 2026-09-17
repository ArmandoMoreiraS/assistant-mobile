import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:ai_companion_app/main.dart';

void main() {
  testWidgets('App renders HomeScreen', (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: AiCompanionApp()));

    expect(find.text('AI Companion'), findsOneWidget);
    expect(find.text('Iniciar conversación'), findsOneWidget);
  });
}
