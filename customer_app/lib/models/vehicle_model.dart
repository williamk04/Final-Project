class VehicleModel {
  final String id;
  final String plateNumber;
  final String userId;

  VehicleModel({
    required this.id,
    required this.plateNumber,
    required this.userId,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'plateNumber': plateNumber,
      'userId': userId,
    };
  }

  factory VehicleModel.fromMap(Map<String, dynamic> map) {
    return VehicleModel(
      id: map['id'] ?? '',
      plateNumber: map['plateNumber'] ?? '',
      userId: map['userId'] ?? '',
    );
  }
}
