// lib/widgets/daily_advice_card.dart
import 'package:flutter/material.dart';
import '../services/api_service.dart';

class DailyAdviceCard extends StatelessWidget {
  final DailyAdviceResponse advice;
  final VoidCallback onPlay;

  const DailyAdviceCard({super.key, required this.advice, required this.onPlay});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1B5E20), Color(0xFF388E3C)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.green.withOpacity(0.3),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text('🌅', style: TextStyle(fontSize: 24)),
              const SizedBox(width: 8),
              Text(
                'आजचे काम',
                style: TextStyle(
                  color: Colors.green[100],
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const Spacer(),
              if (advice.audioUrl != null)
                GestureDetector(
                  onTap: onPlay,
                  child: Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.volume_up, color: Colors.white, size: 28),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            advice.advice,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 20,
              height: 1.5,
              fontWeight: FontWeight.w600,
            ),
          ),
          if (advice.weather.isNotEmpty) ...[
            const SizedBox(height: 10),
            Text(
              '☁️ ${advice.weather}',
              style: TextStyle(
                color: Colors.green[100],
                fontSize: 15,
              ),
            ),
          ],
        ],
      ),
    );
  }
}
