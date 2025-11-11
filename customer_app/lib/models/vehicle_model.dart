class VehicleModel {
  final String id;
  final String plateNumber;
  final String userId;
  final String status; // 👈 thêm field mới

  VehicleModel({
    required this.id,
    required this.plateNumber,
    required this.userId,
    required this.status,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'plateNumber': plateNumber,
      'userId': userId,
      'status': status, // 👈 lưu thêm
    };
  }

  factory VehicleModel.fromMap(Map<String, dynamic> map) {
    return VehicleModel(
      id: map['id'] ?? '',
      plateNumber: map['plateNumber'] ?? '',
      userId: map['userId'] ?? '',
      status: map['status'] ?? 'pending', // 👈 mặc định nếu chưa có
    );
  }
}
