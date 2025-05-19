import 'package:flutter/material.dart';
import 'package:android_app/models/alert.dart';

class AlertDetailPage extends StatelessWidget {
  final Alert alert;
  const AlertDetailPage({super.key, required this.alert});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Alert Details')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              alert.getFormattedTime(),
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 8),
            Text(
              '${alert.node} / ${alert.sensor}',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 16),
            if (alert.imagePath.isNotEmpty)
              Center(
                child: Image.network(
                  alert.getImageUrl(),
                  fit: BoxFit.cover,
                ),
              ),
            const SizedBox(height: 16),
            Text(
              alert.description,
              style: Theme.of(context).textTheme.bodyLarge,
            ),
          ],
        ),
      ),
    );
  }
}
