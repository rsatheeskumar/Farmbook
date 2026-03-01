// lib/screens/onboarding_screen.dart
import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'home_screen.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final _formKey = GlobalKey<FormState>();
  final ApiService _api = ApiService();

  final _phone = TextEditingController();
  final _name = TextEditingController();
  final _village = TextEditingController();
  final _district = TextEditingController();
  final _crop = TextEditingController();
  final _acres = TextEditingController();

  String? _soilType;
  String? _irrigation;
  bool _loading = false;

  Future<void> _register() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);
    try {
      await _api.registerFarm(
        phone: _phone.text.trim(),
        name: _name.text.trim(),
        village: _village.text.trim(),
        district: _district.text.trim(),
        cropName: _crop.text.trim(),
        areaAcres: double.tryParse(_acres.text),
        soilType: _soilType,
        irrigationSource: _irrigation,
      );
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const HomeScreen()),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('नोंदणी झाली नाही. पुन्हा प्रयत्न करा.')),
      );
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: const Color(0xFFF1F8E9),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 16),
                Text(
                  '🌾 किसान साथीत स्वागत आहे',
                  style: theme.textTheme.displayLarge?.copyWith(
                    color: theme.colorScheme.primary,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'एकदा माहिती द्या, बाकी आम्ही सांभाळतो.',
                  style: theme.textTheme.bodyLarge?.copyWith(color: Colors.grey[700]),
                ),
                const SizedBox(height: 28),

                _field(_phone, 'फोन नंबर *', TextInputType.phone, required: true),
                _field(_name, 'आपले नाव', TextInputType.name),
                _field(_village, 'गाव *', TextInputType.text, required: true),
                _field(_district, 'जिल्हा', TextInputType.text),
                _field(_crop, 'सध्याचे पीक (उदा: कापूस, सोयाबीन)', TextInputType.text),
                _field(_acres, 'एकर किती?', TextInputType.number),

                const SizedBox(height: 12),
                Text('माती कोणती?', style: theme.textTheme.bodyLarge),
                const SizedBox(height: 8),
                _chips(['काळी', 'लाल', 'वालुकामय', 'चिकण'], _soilType, (v) {
                  setState(() => _soilType = v);
                }),

                const SizedBox(height: 16),
                Text('पाण्याचा स्रोत?', style: theme.textTheme.bodyLarge),
                const SizedBox(height: 8),
                _chips(['विहीर', 'नळ', 'ठिबक', 'पाऊस'], _irrigation, (v) {
                  setState(() => _irrigation = v);
                }),

                const SizedBox(height: 32),
                SizedBox(
                  width: double.infinity,
                  height: 64,
                  child: ElevatedButton(
                    onPressed: _loading ? null : _register,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: theme.colorScheme.primary,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    child: _loading
                        ? const CircularProgressIndicator(color: Colors.white)
                        : const Text(
                            'सुरू करा →',
                            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                          ),
                  ),
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _field(
    TextEditingController ctrl,
    String label,
    TextInputType type, {
    bool required = false,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: TextFormField(
        controller: ctrl,
        keyboardType: type,
        style: const TextStyle(fontSize: 20),
        decoration: InputDecoration(
          labelText: label,
          labelStyle: const TextStyle(fontSize: 18),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
          filled: true,
          fillColor: Colors.white,
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 18),
        ),
        validator: required
            ? (v) => (v == null || v.isEmpty) ? '$label आवश्यक आहे' : null
            : null,
      ),
    );
  }

  Widget _chips(List<String> options, String? selected, ValueChanged<String?> onSelect) {
    return Wrap(
      spacing: 10,
      runSpacing: 8,
      children: options.map((opt) {
        final isSelected = selected == opt;
        return GestureDetector(
          onTap: () => onSelect(isSelected ? null : opt),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            decoration: BoxDecoration(
              color: isSelected ? const Color(0xFF2E7D32) : Colors.white,
              borderRadius: BorderRadius.circular(30),
              border: Border.all(
                color: isSelected ? const Color(0xFF2E7D32) : Colors.grey.shade400,
                width: 2,
              ),
            ),
            child: Text(
              opt,
              style: TextStyle(
                fontSize: 18,
                color: isSelected ? Colors.white : Colors.black87,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}
