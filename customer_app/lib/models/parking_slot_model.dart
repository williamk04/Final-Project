class ParkingSlotModel {
  final String id;
  final String name;
  final bool isActive;

  ParkingSlotModel({
    required this.id,
    required this.name,
    required this.isActive,
  });

  factory ParkingSlotModel.fromMap(Map<String, dynamic> map, String docId) {
    return ParkingSlotModel(
      id: docId,
      name: map['name'],
      isActive: map['isActive'] ?? true,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      "name": name,
      "isActive": isActive,
    };
  }
}
