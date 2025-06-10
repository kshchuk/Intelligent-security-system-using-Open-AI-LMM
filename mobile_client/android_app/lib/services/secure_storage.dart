import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Secure storage for persisting sensitive data like JWT tokens.
class SecureStorage {
  static const _keyToken = 'auth_token';
  static final _storage = FlutterSecureStorage();

  /// Writes the JWT token to secure storage.
  static Future<void> writeToken(String token) async {
    await _storage.write(key: _keyToken, value: token);
  }

  /// Reads the JWT token from secure storage.
  static Future<String?> readToken() async {
    return await _storage.read(key: _keyToken);
  }

  /// Deletes the JWT token from secure storage.
  static Future<void> deleteToken() async {
    await _storage.delete(key: _keyToken);
  }
}