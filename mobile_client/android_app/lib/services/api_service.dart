import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/io.dart';
import 'package:android_app/models/alert.dart';
import 'package:android_app/settings.dart';

import 'secure_storage.dart';

import '../models/hub.dart';
import '../models/node.dart';
import '../models/sensor.dart';

/// Service class for networking (REST and WebSocket calls to the hub).
class ApiService {
  static String get remote => Settings.remoteBaseUrl;
  
  /// Fetches recent alerts from the REST API (`/alerts` endpoint).
  static Future<List<Alert>> fetchAlerts() async {
    final uri = Uri.parse('${Settings.localBaseUrl}/alerts');
    final token = await SecureStorage.readToken();
    final response = await http.get(
      uri,
      headers: token != null ? {'Authorization': 'Bearer $token'} : <String, String>{},
    );
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Alert.fromJson(json as Map<String, dynamic>)).toList();
    } else {
      throw Exception('Failed to load alerts (HTTP ${response.statusCode})');
    }
  }

  /// Opens a WebSocket connection to the `/ws/alerts` endpoint for live alerts.
  static Future<IOWebSocketChannel> connectAlertsWebSocket() async {
    final token = await SecureStorage.readToken();
    final baseUri = Uri.parse(Settings.localBaseUrl);
    final scheme = baseUri.scheme == 'https' ? 'wss' : 'ws';
    final wsUri = Uri(
      scheme: scheme,
      host: baseUri.host,
      port: baseUri.port,
      path: '/ws/alerts',
    );
    return IOWebSocketChannel.connect(
      wsUri.toString(),
      headers: token != null ? {'Authorization': 'Bearer $token'} : null,
    );
  }

  // Hubs
  static Future<List<Hub>> fetchHubs() async {
    final uri = Uri.parse('$remote/hubs/');
    final token = await SecureStorage.readToken();
    final res = await http.get(
      uri,
      headers: token != null ? {'Authorization': 'Bearer $token'} : <String, String>{},
    );
    if (res.statusCode != 200) throw Exception('Failed to load hubs');
    final List data = jsonDecode(res.body);
    return data.map((j) => Hub.fromJson(j)).toList();
  }

  static Future<Hub> createHub(String name, String ip) async {
    final uri = Uri.parse('$remote/hubs/');
    final token = await SecureStorage.readToken();
    final res = await http.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      },
      body: jsonEncode({'name': name, 'ip': ip}),
    );
    if (res.statusCode != 201) throw Exception('Failed to create hub');
    return Hub.fromJson(jsonDecode(res.body));
  }

  static Future<Hub> updateHub(int id, String name, String ip) async {
    final uri = Uri.parse('$remote/hubs/$id');
    final token = await SecureStorage.readToken();
    final res = await http.put(
      uri,
      headers: {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      },
      body: jsonEncode({'name': name, 'ip': ip}),
    );
    if (res.statusCode != 200) throw Exception('Failed to update hub');
    return Hub.fromJson(jsonDecode(res.body));
  }

  static Future<void> deleteHub(int id) async {
    final uri = Uri.parse('$remote/hubs/$id');
    final token = await SecureStorage.readToken();
    final res = await http.delete(
      uri,
      headers: token != null ? {'Authorization': 'Bearer $token'} : <String, String>{},
    );
    if (res.statusCode != 200) throw Exception('Failed to delete hub');
  }

  // Nodes
  static Future<List<Node>> fetchNodes(int hubId) async {
    final uri = Uri.parse('$remote/hubs/$hubId/nodes');
    final token = await SecureStorage.readToken();
    final res = await http.get(
      uri,
      headers: token != null ? {'Authorization': 'Bearer $token'} : <String, String>{},
    );
    if (res.statusCode != 200) throw Exception('Failed to load nodes');
    final List data = jsonDecode(res.body);
    return data.map((j) => Node.fromJson(j)).toList();
  }
  static Future<Node> createNode(int hubId, String location) async {
    final uri = Uri.parse('$remote/hubs/$hubId/nodes/');
    final token = await SecureStorage.readToken();
    final res = await http.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      },
      body: jsonEncode({'location': location}),
    );
    if (res.  statusCode != 201) throw Exception('Failed to create node');
    return Node.fromJson(jsonDecode(res.body));
  }
  static Future<Node> updateNode(int id, String location) async {
    final uri = Uri.parse('$remote/nodes/$id');
    final token = await SecureStorage.readToken();
    final res = await http.put(
      uri,
      headers: {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      },
      body: jsonEncode({'location': location}),
    );
    if (res.statusCode != 200) throw Exception('Failed to update node');
    return Node.fromJson(jsonDecode(res.body));
  }
  static Future<void> deleteNode(int id) async {
    final uri = Uri.parse('$remote/nodes/$id');
    final token = await SecureStorage.readToken();
    final res = await http.delete(
      uri,
      headers: token != null ? {'Authorization': 'Bearer $token'} : <String, String>{},
    );
    if (res.statusCode != 200) throw Exception('Failed to delete node');
  }

  // Sensors
  static Future<List<Sensor>> fetchSensors(int nodeId) async {
    final uri = Uri.parse('$remote/nodes/$nodeId/sensors');
    final token = await SecureStorage.readToken();
    final res = await http.get(
      uri,
      headers: token != null ? {'Authorization': 'Bearer $token'} : <String, String>{},
    );
    if (res.statusCode != 200) throw Exception('Failed to load sensors');
    final List data = jsonDecode(res.body);
    return data.map((j) => Sensor.fromJson(j)).toList();
  }
  static Future<Sensor> createSensor(int nodeId, String type, String pin) async {
    final uri = Uri.parse('$remote/nodes/$nodeId/sensors/');
    final token = await SecureStorage.readToken();
    final res = await http.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      },
      body: jsonEncode({'type': type, 'pin': pin}),
    );
    if (res.statusCode != 201) throw Exception('Failed to create sensor');
    return Sensor.fromJson(jsonDecode(res.body));
  }
  static Future<Sensor> updateSensor(
      int id, String type, String pin, bool enabled) async {
    final uri = Uri.parse('$remote/sensors/$id');
    final token = await SecureStorage.readToken();
    final res = await http.put(
      uri,
      headers: {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'type': type,
        'pin': pin,
        'status': enabled ? 'enabled' : 'disabled',
      }),
    );
    if (res.statusCode != 200) throw Exception('Failed to update sensor');
    return Sensor.fromJson(jsonDecode(res.body));
  }

  static Future<void> deleteSensor(int id) async {
    final uri = Uri.parse('$remote/sensors/$id');
    final token = await SecureStorage.readToken();
    final res = await http.delete(
      uri,
      headers: token != null ? {'Authorization': 'Bearer $token'} : <String, String>{},
    );
    if (res.statusCode != 200) throw Exception('Failed to delete sensor');
  }

  /// Registers a new user account.
  static Future<void> registerUser(String username, String password, {String? email}) async {
    final uri = Uri.parse('$remote/auth/register');
    final body = <String, dynamic>{'username': username, 'password': password};
    if (email != null) body['email'] = email;
    final res = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    );
    if (res.statusCode != 200) {
      throw Exception('Registration failed (HTTP ${res.statusCode})');
    }
  }

  /// Authenticates the user and stores the JWT token.
  static Future<void> login(String username, String password) async {
    final uri = Uri.parse('$remote/auth/token');
    final res = await http.post(
      uri,
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: 'username=${Uri.encodeComponent(username)}&password=${Uri.encodeComponent(password)}',
    );
    if (res.statusCode != 200) {
      throw Exception('Login failed (HTTP ${res.statusCode})');
    }
    final data = jsonDecode(res.body) as Map<String, dynamic>;
    final token = data['access_token'] as String?;
    if (token == null) throw Exception('Token not found in response');
    await SecureStorage.writeToken(token);
  }

}
