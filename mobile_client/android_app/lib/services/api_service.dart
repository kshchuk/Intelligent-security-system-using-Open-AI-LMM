import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/io.dart';
import 'package:android_app/models/alert.dart';
import 'package:android_app/settings.dart';

/// Service class for networking (REST and WebSocket calls to the hub).
class ApiService {
  /// Fetches recent alerts from the REST API (`/alerts` endpoint).
  static Future<List<Alert>> fetchAlerts() async {
    final uri = Uri.parse('${Settings.baseUrl}/alerts');
    final response = await http.get(uri);
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Alert.fromJson(json as Map<String, dynamic>)).toList();
    } else {
      throw Exception('Failed to load alerts (HTTP ${response.statusCode})');
    }
  }

  /// Opens a WebSocket connection to the `/ws/alerts` endpoint for live alerts.
  static IOWebSocketChannel connectAlertsWebSocket() {
    final baseUri = Uri.parse(Settings.baseUrl);
    final scheme = baseUri.scheme == 'https' ? 'wss' : 'ws';
    final wsUri = Uri(
      scheme: scheme,
      host: baseUri.host,
      port: baseUri.port,
      path: '/ws/alerts',
    );
    return IOWebSocketChannel.connect(wsUri);
  }
}
