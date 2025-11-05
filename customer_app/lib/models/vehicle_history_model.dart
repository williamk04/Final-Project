class VehicleHistoryModel {
  final String licensePlate;
  final String imageUrl;
  final String? exitImageUrl;
  final String entryTime;
  final String? exitTime;
  final int? fee;
  final int durationMinutes;
  final String status;

  VehicleHistoryModel({
    required this.licensePlate,
    required this.imageUrl,
    this.exitImageUrl,
    required this.entryTime,
    this.exitTime,
    this.fee,
    required this.durationMinutes,
    required this.status,
  });

  factory VehicleHistoryModel.fromMap(Map<String, dynamic> map) {
    return VehicleHistoryModel(
      licensePlate: map['license_plate'] ?? '',
      imageUrl: map['image_url'] ?? '',
      exitImageUrl: map['exit_image_url'],
      entryTime: map['entry_time'] ?? '',
      exitTime: map['exit_time'],
      fee: map['fee'],
      durationMinutes: map['duration_minutes'] ?? 0,
      status: map['status'] ?? '',
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'license_plate': licensePlate,
      'image_url': imageUrl,
      'exit_image_url': exitImageUrl,
      'entry_time': entryTime,
      'exit_time': exitTime,
      'fee': fee,
      'duration_minutes': durationMinutes,
      'status': status,
    };
  }
}
