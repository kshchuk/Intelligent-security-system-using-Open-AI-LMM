import 'package:flutter/material.dart';
import 'package:android_app/services/api_service.dart';
import 'package:android_app/services/secure_storage.dart';
import 'package:android_app/main.dart';

/// Login and registration screen for user authentication.
class LoginPage extends StatefulWidget {
  const LoginPage({Key? key}) : super(key: key);
  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _usernameCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  bool _loading = false;

  Future<void> _authenticate({required bool register}) async {
    setState(() => _loading = true);
    try {
      if (register) {
        await ApiService.registerUser(
          _usernameCtrl.text.trim(),
          _passwordCtrl.text,
        );
      }
      await ApiService.login(
        _usernameCtrl.text.trim(),
        _passwordCtrl.text,
      );
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const HomePage()),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('${register ? 'Registration' : 'Login'} failed: $e')),
      );
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Login / Register')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: _usernameCtrl,
              decoration: const InputDecoration(labelText: 'Username'),
            ),
            TextField(
              controller: _passwordCtrl,
              decoration: const InputDecoration(labelText: 'Password'),
              obscureText: true,
            ),
            const SizedBox(height: 20),
            if (_loading)
              const CircularProgressIndicator()
            else ...[
              ElevatedButton(
                onPressed: () => _authenticate(register: false),
                child: const Text('Login'),
              ),
              TextButton(
                onPressed: () => _authenticate(register: true),
                child: const Text('Register'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}