import 'package:android_app/settings.dart';

class Hub {
  final int id;
  final String name;
  final String ip;

  Hub({required this.id, required this.name, required this.ip});

  factory Hub.fromJson(Map<String, dynamic> json) {
    return Hub(
      id: json['id'] as int,
      name: json['name'] as String,
      ip: json['ip'] as String,
    );
  }

  Map<String, dynamic> toJson() => {
    'name': name,
    'ip': ip,
  };
}
