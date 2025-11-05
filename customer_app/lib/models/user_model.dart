class UserModel {
  final String uid;
  final String name;
  final String email;
  final List<String> vehicles;

  UserModel({
    required this.uid,
    required this.name,
    required this.email,
    required this.vehicles,
  });

  Map<String, dynamic> toMap() {
    return {
      'uid': uid,
      'name': name,
      'email': email,
      'vehicles': vehicles,
    };
  }

  factory UserModel.fromMap(Map<String, dynamic> map) {
    return UserModel(
      uid: map['uid'],
      name: map['name'],
      email: map['email'],
      vehicles: List<String>.from(map['vehicles'] ?? []),
    );
  }
}
