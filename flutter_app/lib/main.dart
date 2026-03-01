// lib/main.dart
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'screens/home_screen.dart';
import 'screens/onboarding_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  final isRegistered = prefs.getString('farm_id') != null;

  runApp(KisanSaathiApp(isRegistered: isRegistered));
}

class KisanSaathiApp extends StatelessWidget {
  final bool isRegistered;
  const KisanSaathiApp({super.key, required this.isRegistered});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'किसान साथी',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF2E7D32), // Deep green
          primary: const Color(0xFF2E7D32),
          secondary: const Color(0xFFFFA000), // Amber
          background: const Color(0xFFF1F8E9),
        ),
        textTheme: const TextTheme(
          displayLarge: TextStyle(
            fontFamily: 'NotoSansDevanagari',
            fontSize: 28,
            fontWeight: FontWeight.bold,
          ),
          bodyLarge: TextStyle(
            fontFamily: 'NotoSansDevanagari',
            fontSize: 20,
          ),
          bodyMedium: TextStyle(
            fontFamily: 'NotoSansDevanagari',
            fontSize: 18,
          ),
        ),
        useMaterial3: true,
      ),
      home: isRegistered ? const HomeScreen() : const OnboardingScreen(),
    );
  }
}
