class Sensor {
  final int id;
  final int nodeId;
  final String type;
  final String pin;
  bool alertEnabled;

  Sensor({
    required this.id,
    required this.nodeId,
    required this.type,
    required this.pin,
    required this.alertEnabled,
  });

  factory Sensor.fromJson(Map<String, dynamic> json) {
    return Sensor(
      id: json['id'] as int,
      nodeId: json['node_id'] as int,
      type: json['type'] as String,
      pin: json['pin'] as String,
      alertEnabled: (json['status'] as String? ?? 'disabled') == 'enabled',
    );
  }

  Map<String, dynamic> toJson() => {
    'type': type,
    'pin': pin,
    'status': alertEnabled ? 'enabled' : 'disabled',
  };
}