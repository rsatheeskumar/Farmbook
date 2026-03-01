// lib/widgets/response_card.dart
import 'package:flutter/material.dart';

class ResponseCard extends StatelessWidget {
  final String? question;
  final String advice;
  final bool isPlaying;
  final VoidCallback onPlayTap;

  const ResponseCard({
    super.key,
    this.question,
    required this.advice,
    required this.isPlaying,
    required this.onPlayTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFF2E7D32), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.15),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (question != null && question!.isNotEmpty) ...[
            Row(
              children: [
                const Icon(Icons.person, color: Color(0xFF2E7D32), size: 22),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    question!,
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey[700],
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ),
              ],
            ),
            const Divider(height: 20),
          ],
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('🌾', style: TextStyle(fontSize: 24)),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  advice,
                  style: const TextStyle(
                    fontSize: 20,
                    height: 1.6,
                    fontWeight: FontWeight.w600,
                    color: Colors.black87,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          SizedBox(
            width: double.infinity,
            height: 52,
            child: ElevatedButton.icon(
              onPressed: onPlayTap,
              icon: Icon(isPlaying ? Icons.pause : Icons.play_arrow, size: 28),
              label: Text(
                isPlaying ? 'थांबवा' : '🔊 ऐका',
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: isPlaying ? Colors.orange : const Color(0xFF2E7D32),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
