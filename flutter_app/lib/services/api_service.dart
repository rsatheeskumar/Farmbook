// lib/services/api_service.dart
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String _baseUrl = 'http://YOUR_SERVER_IP:8000'; // Change this

  Future<String> get baseUrl async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('api_url') ?? _baseUrl;
  }

  Future<String?> get farmId async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('farm_id');
  }

  Future<String?> get userId async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('user_id');
  }

  // Register a new farm
  Future<Map<String, dynamic>> registerFarm({
    required String phone,
    String? name,
    String? village,
    String? taluka,
    String? district,
    double? areaAcres,
    String? soilType,
    String? irrigationSource,
    String? cropName,
    String? sowingDate,
  }) async {
    final url = await baseUrl;
    final resp = await http.post(
      Uri.parse('$url/register-farm'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'phone': phone,
        'name': name,
        'village': village,
        'taluka': taluka,
        'district': district,
        'area_acres': areaAcres,
        'soil_type': soilType,
        'irrigation_source': irrigationSource,
        'crop_name': cropName,
        'sowing_date': sowingDate,
      }),
    );

    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body);
      // Persist IDs
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('farm_id', data['farm_id']);
      await prefs.setString('user_id', data['user_id']);
      return data;
    }
    throw Exception('Farm registration failed: ${resp.body}');
  }

  // Send voice recording for advice
  Future<VoiceResponse?> sendVoice(File audioFile) async {
    final url = await baseUrl;
    final fId = await farmId;
    final uId = await userId;

    if (fId == null || uId == null) {
      throw Exception('Not registered. Please set up your farm first.');
    }

    final request = http.MultipartRequest('POST', Uri.parse('$url/voice-input'));
    request.fields['farm_id'] = fId;
    request.fields['user_id'] = uId;
    request.files.add(await http.MultipartFile.fromPath('audio', audioFile.path));

    final streamed = await request.send().timeout(const Duration(seconds=60));
    final resp = await http.Response.fromStream(streamed);

    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body);
      return VoiceResponse(
        question: data['question'] ?? '',
        advice: data['advice'] ?? '',
        audioUrl: data['audio_url'],
      );
    }
    throw Exception('Voice request failed: ${resp.body}');
  }

  // Send crop photo for diagnosis
  Future<DiagnosisResponse?> sendImage(File imageFile) async {
    final url = await baseUrl;
    final fId = await farmId;
    final uId = await userId;

    if (fId == null || uId == null) {
      throw Exception('Not registered.');
    }

    final request = http.MultipartRequest('POST', Uri.parse('$url/image-diagnosis'));
    request.fields['farm_id'] = fId;
    request.fields['user_id'] = uId;
    request.files.add(await http.MultipartFile.fromPath('image', imageFile.path));

    final streamed = await request.send().timeout(const Duration(seconds=60));
    final resp = await http.Response.fromStream(streamed);

    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body);
      return DiagnosisResponse(
        diagnosis: data['diagnosis'] ?? '',
        audioUrl: data['audio_url'],
      );
    }
    throw Exception('Image diagnosis failed: ${resp.body}');
  }

  // Get today's daily advice
  Future<DailyAdviceResponse?> getDailyAdvice() async {
    final url = await baseUrl;
    final fId = await farmId;

    if (fId == null) return null;

    final resp = await http.get(
      Uri.parse('$url/daily-advice/$fId'),
    ).timeout(const Duration(seconds=30));

    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body);
      return DailyAdviceResponse(
        date: data['date'] ?? '',
        advice: data['advice'] ?? '',
        audioUrl: data['audio_url'],
        weather: data['weather'] ?? '',
      );
    }
    return null;
  }

  // Get farm memory/profile
  Future<Map<String, dynamic>?> getFarmMemory() async {
    final url = await baseUrl;
    final fId = await farmId;
    if (fId == null) return null;

    final resp = await http.get(Uri.parse('$url/farm-memory/$fId'));
    if (resp.statusCode == 200) return jsonDecode(resp.body);
    return null;
  }
}

class VoiceResponse {
  final String question;
  final String advice;
  final String? audioUrl;
  VoiceResponse({required this.question, required this.advice, this.audioUrl});
}

class DiagnosisResponse {
  final String diagnosis;
  final String? audioUrl;
  DiagnosisResponse({required this.diagnosis, this.audioUrl});
}

class DailyAdviceResponse {
  final String date;
  final String advice;
  final String? audioUrl;
  final String weather;
  DailyAdviceResponse({
    required this.date,
    required this.advice,
    this.audioUrl,
    required this.weather,
  });
}
