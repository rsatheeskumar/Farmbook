// lib/screens/home_screen.dart
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';
import '../widgets/daily_advice_card.dart';
import '../widgets/mic_button.dart';
import '../widgets/response_card.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiService _api = ApiService();
  final AudioService _audio = AudioService();
  final ImagePicker _picker = ImagePicker();

  bool _isRecording = false;
  bool _isLoading = false;
  bool _isPlaying = false;

  String? _lastQuestion;
  String? _lastAdvice;
  String? _lastAudioUrl;
  DailyAdviceResponse? _dailyAdvice;

  @override
  void initState() {
    super.initState();
    _loadDailyAdvice();
    _audio.playerStateStream.listen((state) {
      if (mounted) {
        setState(() {
          _isPlaying = state == PlayerState.playing;
        });
      }
    });
  }

  @override
  void dispose() {
    _audio.dispose();
    super.dispose();
  }

  Future<void> _loadDailyAdvice() async {
    try {
      final advice = await _api.getDailyAdvice();
      if (mounted) setState(() => _dailyAdvice = advice);
    } catch (_) {}
  }

  // ---- VOICE RECORDING ----
  Future<void> _handleMicTap() async {
    if (_isLoading) return;

    if (_isRecording) {
      // Stop and upload
      final file = await _audio.stopRecording();
      setState(() => _isRecording = false);
      if (file != null) await _uploadAudio(file);
    } else {
      final ok = await _audio.requestPermission();
      if (!ok) {
        _showSnack('मायक्रोफोन परवानगी द्या');
        return;
      }
      await _audio.startRecording();
      setState(() => _isRecording = true);
    }
  }

  Future<void> _uploadAudio(File file) async {
    setState(() => _isLoading = true);
    try {
      final resp = await _api.sendVoice(file);
      if (resp != null && mounted) {
        setState(() {
          _lastQuestion = resp.question;
          _lastAdvice = resp.advice;
          _lastAudioUrl = resp.audioUrl;
        });
        // Auto-play response
        if (resp.audioUrl != null) {
          await _audio.playUrl(resp.audioUrl!);
        }
      }
    } catch (e) {
      _showSnack('माफ करा, पुन्हा प्रयत्न करा');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  // ---- CAMERA / IMAGE ----
  Future<void> _handleCameraTap() async {
    if (_isLoading) return;
    final XFile? img = await _picker.pickImage(
      source: ImageSource.camera,
      imageQuality: 70,
      maxWidth: 1200,
    );
    if (img == null) return;

    setState(() => _isLoading = true);
    try {
      final resp = await _api.sendImage(File(img.path));
      if (resp != null && mounted) {
        setState(() {
          _lastAdvice = resp.diagnosis;
          _lastAudioUrl = resp.audioUrl;
        });
        if (resp.audioUrl != null) {
          await _audio.playUrl(resp.audioUrl!);
        }
      }
    } catch (e) {
      _showSnack('फोटो पाठवता आला नाही');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  // ---- PLAYBACK ----
  Future<void> _playLastResponse() async {
    if (_lastAudioUrl == null) return;
    if (_isPlaying) {
      await _audio.stop();
    } else {
      await _audio.playUrl(_lastAudioUrl!);
    }
  }

  void _showSnack(String msg) {
    ScaffoldMessenger.of(context)
        .showSnackBar(SnackBar(content: Text(msg, style: const TextStyle(fontSize: 18))));
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: theme.colorScheme.background,
      appBar: AppBar(
        backgroundColor: theme.colorScheme.primary,
        title: const Text(
          '🌾 किसान साथी',
          style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white, size: 28),
            onPressed: _loadDailyAdvice,
          )
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              // Daily advice card
              if (_dailyAdvice != null)
                DailyAdviceCard(
                  advice: _dailyAdvice!,
                  onPlay: () {
                    if (_dailyAdvice!.audioUrl != null) {
                      _audio.playUrl(_dailyAdvice!.audioUrl!);
                    }
                  },
                ),
              const SizedBox(height: 24),

              // Last response card
              if (_lastAdvice != null)
                ResponseCard(
                  question: _lastQuestion,
                  advice: _lastAdvice!,
                  isPlaying: _isPlaying,
                  onPlayTap: _playLastResponse,
                ),

              const SizedBox(height: 32),

              // Loading indicator
              if (_isLoading)
                Column(
                  children: [
                    const CircularProgressIndicator(),
                    const SizedBox(height: 12),
                    Text('सल्ला येतो आहे...', style: theme.textTheme.bodyLarge),
                  ],
                ),

              const SizedBox(height: 16),

              // MIC BUTTON (main CTA)
              MicButton(
                isRecording: _isRecording,
                isLoading: _isLoading,
                onTap: _handleMicTap,
              ),

              const SizedBox(height: 12),

              Text(
                _isRecording ? 'बोला...' : 'बोलण्यासाठी दाबा',
                style: theme.textTheme.bodyLarge?.copyWith(
                  color: _isRecording ? Colors.red : Colors.grey[700],
                  fontWeight: FontWeight.w600,
                ),
              ),

              const SizedBox(height: 32),

              // Camera button
              SizedBox(
                width: double.infinity,
                height: 70,
                child: ElevatedButton.icon(
                  onPressed: _isLoading ? null : _handleCameraTap,
                  icon: const Icon(Icons.camera_alt, size: 32),
                  label: const Text(
                    '📸 पीक फोटो पाठवा',
                    style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFFFA000),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
