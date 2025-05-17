import 'package:flutter/material.dart';
import 'package:android_app/settings.dart';
import 'package:android_app/models/alert.dart';
import 'package:android_app/services/api_service.dart';
import 'package:android_app/screens/alerts_page.dart';
import 'package:android_app/screens/stream_page.dart';

void main() {
  runApp(const MyApp());
}

/// Root widget of the application.
class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'IoT Security Hub',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
      ),
      home: const HomePage(),
    );
  }
}

/// Home page with bottom navigation for Alerts and Live Stream.
class HomePage extends StatefulWidget {
  const HomePage({super.key});
  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _currentIndex = 0;

  /// Opens a dialog to change the hub IP/domain.
  Future<void> _openSettingsDialog() async {
    final TextEditingController ctrl =
    TextEditingController(text: Settings.baseUrl);
    final oldUrl = Settings.baseUrl;
    bool? saved = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Set Hub Address'),
          content: TextField(
            controller: ctrl,
            decoration: const InputDecoration(labelText: "Hub IP or URL"),
            autofocus: true,
          ),
          actions: [
            TextButton(
              child: const Text('Cancel'),
              onPressed: () => Navigator.pop(context, false),
            ),
            TextButton(
              child: const Text('Save'),
              onPressed: () {
                String input = ctrl.text.trim();
                if (input.isNotEmpty) {
                  // Ensure the URL has a scheme
                  if (!input.startsWith('http://') &&
                      !input.startsWith('https://')) {
                    input = 'http://$input';
                  }
                  Settings.baseUrl = input;
                }
                Navigator.pop(context, true);
              },
            ),
          ],
        );
      },
    );
    // If saved and changed, rebuild to apply new settings
    if (saved == true && Settings.baseUrl != oldUrl) {
      setState(() {
        // Rebuild will recreate pages with new Settings.baseUrl via keys
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    // Titles for the two screens
    final titles = ["Alerts", "Live Stream"];
    return Scaffold(
      appBar: AppBar(
        title: Text(titles[_currentIndex]),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: _openSettingsDialog,
          ),
        ],
      ),
      body: (_currentIndex == 0)
          ? AlertsPage(key: ValueKey(Settings.baseUrl))
          : StreamPage(key: ValueKey(Settings.baseUrl)),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() {
          _currentIndex = index;
        }),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.list), label: 'Alerts'),
          BottomNavigationBarItem(icon: Icon(Icons.videocam), label: 'Stream'),
        ],
      ),
    );
  }
}
