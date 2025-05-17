import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/io.dart';
import 'package:android_app/models/alert.dart';
import 'package:android_app/services/api_service.dart';
import 'package:android_app/settings.dart';

/// Screen showing the list of alerts with timestamps, images, and descriptions.
class AlertsPage extends StatefulWidget {
  const AlertsPage({super.key});
  @override
  State<AlertsPage> createState() => _AlertsPageState();
}

class _AlertsPageState extends State<AlertsPage> {
  List<Alert> _alerts = [];
  bool _loading = true;
  IOWebSocketChannel? _channel;
  StreamSubscription? _wsSubscription;

  /// Load recent alerts via REST API and then connect to WebSocket for updates.
  void _initAlerts() async {
    try {
      final alerts = await ApiService.fetchAlerts();
      setState(() {
        _alerts = alerts;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _loading = false;
      });
      // Optionally handle error (e.g., show a message)
    }
    // Connect to WebSocket after initial fetch
    _channel = ApiService.connectAlertsWebSocket();
    _wsSubscription = _channel!.stream.listen((message) {
      // Parse incoming alert JSON
      final Map<String, dynamic> data = jsonDecode(message);
      final newAlert = Alert.fromJson(data);
      // Avoid duplicate if already in list (e.g., if just fetched)
      final exists = _alerts.any((alert) => alert.imagePath == newAlert.imagePath);
      if (!exists) {
        setState(() {
          _alerts.insert(0, newAlert);  // newest alert at top
        });
      }
    }, onError: (error) {
      // Handle WebSocket error if necessary
      debugPrint("WebSocket error: $error");
    });
  }

  @override
  void initState() {
    super.initState();
    _initAlerts();
  }

  @override
  void dispose() {
    _wsSubscription?.cancel();
    _channel?.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_alerts.isEmpty) {
      return const Center(child: Text('No alerts yet.'));
    }
    // List of alert cards
    return ListView.builder(
      padding: const EdgeInsets.all(8.0),
      itemCount: _alerts.length,
      itemBuilder: (context, index) {
        final alert = _alerts[index];
        return Card(
          margin: const EdgeInsets.symmetric(vertical: 4),
          child: ListTile(
            leading: alert.imagePath.isNotEmpty
                ? Image.network(
              alert.getImageUrl(),
              width: 60,
              height: 60,
              fit: BoxFit.cover,
            )
                : null,
            title: Text(alert.description),
            subtitle: Text('${alert.node}/${alert.sensor} — ${alert.getFormattedTime()}'),
          ),
        );
      },
    );
  }
}
