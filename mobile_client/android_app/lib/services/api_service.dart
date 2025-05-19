import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/io.dart';
import 'package:android_app/models/alert.dart';
import 'package:android_app/settings.dart';

import '../models/hub.dart';
import '../models/node.dart';
import '../models/sensor.dart';

/// Service class for networking (REST and WebSocket calls to the hub).
class ApiService {
  static String get remote => Settings.remoteBaseUrl;
  
  /// Fetches recent alerts from the REST API (`/alerts` endpoint).
  static Future<List<Alert>> fetchAlerts() async {
    final uri = Uri.parse('${Settings.localBaseUrl}/alerts');
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
    final baseUri = Uri.parse(Settings.localBaseUrl);
    final scheme = baseUri.scheme == 'https' ? 'wss' : 'ws';
    final wsUri = Uri(
      scheme: scheme,
      host: baseUri.host,
      port: baseUri.port,
      path: '/ws/alerts',
    );
    return IOWebSocketChannel.connect(wsUri);
  }

  // Hubs
  static Future<List<Hub>> fetchHubs() async {
    final res = await http.get(Uri.parse('$remote/hubs/'));
    if (res.statusCode != 200) throw Exception('Failed to load hubs');
    final List data = jsonDecode(res.body);
    return data.map((j) => Hub.fromJson(j)).toList();
  }

  static Future<Hub> createHub(String name, String ip) async {
    final res = await http.post(
      Uri.parse('$remote/hubs/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'name': name, 'ip': ip}),
    );
    if (res.statusCode != 201) throw Exception('Failed to create hub');
    return Hub.fromJson(jsonDecode(res.body));
  }

  static Future<Hub> updateHub(int id, String name, String ip) async {
    final res = await http.put(
      Uri.parse('$remote/hubs/$id'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'name': name, 'ip': ip}),
    );
    if (res.statusCode != 200) throw Exception('Failed to update hub');
    return Hub.fromJson(jsonDecode(res.body));
  }

  static Future<void> deleteHub(int id) async {
    final res = await http.delete(Uri.parse('$remote/hubs/$id'));
    if (res.statusCode != 200) throw Exception('Failed to delete hub');
  }

  // Nodes
  static Future<List<Node>> fetchNodes(int hubId) async {
    final res = await http.get(Uri.parse('$remote/hubs/$hubId/nodes'));
    if (res.statusCode != 200) throw Exception('Failed to load nodes');
    final List data = jsonDecode(res.body);
    return data.map((j) => Node.fromJson(j)).toList();
  }
  static Future<Node> createNode(int hubId, String location) async {
    final res = await http.post(
      Uri.parse('$remote/hubs/$hubId/nodes'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'location': location}),
    );
    if (res.statusCode != 201) throw Exception('Failed to create node');
    return Node.fromJson(jsonDecode(res.body));
  }
  static Future<Node> updateNode(int id, String location) async {
    final res = await http.put(
      Uri.parse('$remote/nodes/$id'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'location': location}),
    );
    if (res.statusCode != 200) throw Exception('Failed to update node');
    return Node.fromJson(jsonDecode(res.body));
  }
  static Future<void> deleteNode(int id) async {
    final res = await http.delete(Uri.parse('$remote/nodes/$id'));
    if (res.statusCode != 200) throw Exception('Failed to delete node');
  }

  // Sensors
  static Future<List<Sensor>> fetchSensors(int nodeId) async {
    final res = await http.get(Uri.parse('$remote/nodes/$nodeId/sensors'));
    if (res.statusCode != 200) throw Exception('Failed to load sensors');
    final List data = jsonDecode(res.body);
    return data.map((j) => Sensor.fromJson(j)).toList();
  }
  static Future<Sensor> createSensor(int nodeId, String type, String pin) async {
    final res = await http.post(
      Uri.parse('$remote/nodes/$nodeId/sensors'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'type': type, 'pin': pin}),
    );
    if (res.statusCode != 201) throw Exception('Failed to create sensor');
    return Sensor.fromJson(jsonDecode(res.body));
  }
  static Future<Sensor> updateSensor(int id, String type, String pin) async {
    final res = await http.put(
      Uri.parse('$remote/sensors/$id'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'type': type, 'pin': pin}),
    );
    if (res.statusCode != 200) throw Exception('Failed to update sensor');
    return Sensor.fromJson(jsonDecode(res.body));
  }
  static Future<void> deleteSensor(int id) async {
    final res = await http.delete(Uri.parse('$remote/sensors/$id'));
    if (res.statusCode != 200) throw Exception('Failed to delete sensor');
  }
}
