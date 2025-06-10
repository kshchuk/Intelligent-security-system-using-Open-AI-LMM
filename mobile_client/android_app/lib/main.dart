import 'package:android_app/settings.dart';
import 'package:android_app/screens/alerts_page.dart';
import 'package:android_app/screens/stream_page.dart';
import 'package:android_app/screens/hub_list_page.dart';

import 'package:flutter/material.dart';
import 'package:android_app/services/secure_storage.dart';
import 'package:android_app/screens/login_page.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MyApp());
}

/// Root widget of the application.
class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return FutureBuilder<String?>(
      future: SecureStorage.readToken(),
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const MaterialApp(home: Scaffold(body: Center(child: CircularProgressIndicator())));
        }
        final loggedIn = snapshot.data != null;
        return MaterialApp(
          title: 'IoT Security Hub',
          theme: ThemeData(
            colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
          ),
          home: loggedIn ? const HomePage() : const LoginPage(),
        );
      },
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
    TextEditingController(text: Settings.localBaseUrl);
    final oldUrl = Settings.localBaseUrl;
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
                  Settings.localBaseUrl = input;
                }
                Navigator.pop(context, true);
              },
            ),
          ],
        );
      },
    );
    // If saved and changed, rebuild to apply new settings
    if (saved == true && Settings.localBaseUrl != oldUrl) {
      setState(() {
        // Rebuild will recreate pages with new Settings.baseUrl via keys
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    // Titles for the two screens
    final titles = ['Alerts','Live Stream','Hubs'];
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
      body: switch (_currentIndex) {
        0 => AlertsPage(key: ValueKey(Settings.localBaseUrl)),
        1 => StreamPage(key: ValueKey(Settings.localBaseUrl)),
        2 => HubListPage(key: ValueKey(Settings.localBaseUrl)),
        _ => const Center(child: Text('Unknown page')),
      },
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() {
          _currentIndex = index;
        }),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.list), label: 'Alerts'),
          BottomNavigationBarItem(icon: Icon(Icons.videocam), label: 'Stream'),
          BottomNavigationBarItem(icon:Icon(Icons.device_hub),label:'Hubs'),
        ],
      ),
    );
  }
}
