import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:web_socket_channel/io.dart';

import 'package:android_app/models/alert.dart';
import 'package:android_app/services/api_service.dart';
import 'package:android_app/screens/alert_detail_page.dart';

class AlertsPage extends StatefulWidget {
  const AlertsPage({super.key});
  @override
  State<AlertsPage> createState() => _AlertsPageState();
}

class _AlertsPageState extends State<AlertsPage> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  List<Alert> _historyAlerts = [];
  List<Alert> _newAlerts = [];
  bool _loading = true;

  IOWebSocketChannel? _channel;
  StreamSubscription? _wsSub;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _initAlerts();
  }

  @override
  void dispose() {
    _wsSub?.cancel();
    _channel?.sink.close();
    _tabController.dispose();
    super.dispose();
  }

  void _initAlerts() async {
    // 1) Load history via REST
    try {
      final alerts = await ApiService.fetchAlerts();
      setState(() {
        _historyAlerts = alerts;
        _loading = false;
      });
    } catch (_) {
      setState(() => _loading = false);
    }

    // 2) Subscribe to WebSocket for new alerts
    _channel = ApiService.connectAlertsWebSocket();
    _wsSub = _channel!.stream.listen((msg) {
      final data = jsonDecode(msg);
      final a = Alert.fromJson(data);
      final inHist = _historyAlerts.any((x) => x.imagePath == a.imagePath);
      final inNew  = _newAlerts.any((x) => x.imagePath == a.imagePath);
      if (!inHist && !inNew) {
        setState(() => _newAlerts.insert(0, a));
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Column(
      children: [
        TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'New'),
            Tab(text: 'History'),
          ],
        ),
        Expanded(
          child: TabBarView(
            controller: _tabController,
            children: [
              _buildList(_newAlerts, isNew: true),
              _buildList(_historyAlerts, isNew: false),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildList(List<Alert> alerts, {required bool isNew}) {
    if (alerts.isEmpty) {
      return Center(child: Text(isNew ? 'No new alerts.' : 'No history alerts.'));
    }
    return ListView.builder(
      padding: const EdgeInsets.all(8),
      itemCount: alerts.length,
      itemBuilder: (ctx, i) {
        final alert = alerts[i];
        final shortDesc = alert.description.length > 50
            ? '${alert.description.substring(0, 50)}...'
            : alert.description;

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
            title: Text(shortDesc),
            subtitle: Text(alert.getFormattedTime()),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              // navigate to detail
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => AlertDetailPage(alert: alert),
                ),
              );
              // if it was new, mark as read
              if (isNew) {
                setState(() {
                  _newAlerts.removeAt(i);
                  _historyAlerts.insert(0, alert);
                });
              }
            },
          ),
        );
      },
    );
  }
}
