class Node {
  final int id;
  final int hubId;
  final String location;

  Node({required this.id, required this.hubId, required this.location});

  factory Node.fromJson(Map<String, dynamic> json) {
    return Node(
      id: json['id'] as int,
      hubId: json['hub_id'] as int,
      location: json['location'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() => {
    'location': location,
  };
}