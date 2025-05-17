import 'package:android_app/settings.dart';

class Alert {
  final int? id;
  final DateTime timestamp;
  final String node;
  final String sensor;
  final String imagePath;
  final String description;

  Alert({
    this.id,
    required this.timestamp,
    required this.node,
    required this.sensor,
    required this.imagePath,
    required this.description,
  });

  /// Factory to create an Alert from JSON (as received from the API).
  factory Alert.fromJson(Map<String, dynamic> json) {
    return Alert(
      id: json.containsKey('id') ? json['id'] as int? : null,
      timestamp: DateTime.parse(json['timestamp'] as String),
      node: json['node'] as String? ?? '',
      sensor: json['sensor'] as String? ?? '',
      imagePath: json['image_path'] as String? ?? '',
      description: json['description'] as String? ?? '',
    );
  }

  /// Full URL to the alert's image, combining the hub address and image path.
  String getImageUrl() {
    return '${Settings.baseUrl}/$imagePath';
  }

  /// Formatted timestamp for display (YYYY-MM-DD HH:MM:SS).
  String getFormattedTime() {
    return timestamp.toLocal().toString().split('.')[0];
  }
}
