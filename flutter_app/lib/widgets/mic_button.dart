// lib/widgets/mic_button.dart
import 'package:flutter/material.dart';

class MicButton extends StatefulWidget {
  final bool isRecording;
  final bool isLoading;
  final VoidCallback onTap;

  const MicButton({
    super.key,
    required this.isRecording,
    required this.isLoading,
    required this.onTap,
  });

  @override
  State<MicButton> createState() => _MicButtonState();
}

class _MicButtonState extends State<MicButton> with SingleTickerProviderStateMixin {
  late AnimationController _pulseCtrl;
  late Animation<double> _pulseAnim;

  @override
  void initState() {
    super.initState();
    _pulseCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    )..repeat(reverse: true);
    _pulseAnim = Tween<double>(begin: 1.0, end: 1.12).animate(
      CurvedAnimation(parent: _pulseCtrl, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _pulseCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isRecording = widget.isRecording;
    final isLoading = widget.isLoading;

    return GestureDetector(
      onTap: isLoading ? null : widget.onTap,
      child: AnimatedBuilder(
        animation: _pulseAnim,
        builder: (context, child) {
          return Transform.scale(
            scale: isRecording ? _pulseAnim.value : 1.0,
            child: Container(
              width: 180,
              height: 180,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isRecording
                    ? Colors.red
                    : isLoading
                        ? Colors.grey
                        : const Color(0xFF2E7D32),
                boxShadow: [
                  BoxShadow(
                    color: (isRecording ? Colors.red : const Color(0xFF2E7D32))
                        .withOpacity(0.4),
                    blurRadius: 24,
                    spreadRadius: 8,
                  ),
                ],
              ),
              child: Icon(
                isRecording ? Icons.stop : Icons.mic,
                size: 80,
                color: Colors.white,
              ),
            ),
          );
        },
      ),
    );
  }
}
