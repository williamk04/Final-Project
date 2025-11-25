import 'package:cloud_firestore/cloud_firestore.dart';

class ReservationModel {
  final String id;
  final String slotId;
  final String plateNumber;
  final String userId;
  final DateTime startTime;
  final DateTime endTime;
  final DateTime createdAt;
  final int paidFee;
  final String status;

  ReservationModel({
    required this.id,
    required this.slotId,
    required this.plateNumber,
    required this.userId,
    required this.startTime,
    required this.endTime,
    required this.createdAt,
    required this.paidFee,
    required this.status,
  });

  Map<String, dynamic> toMap() {
    return {
      "id": id,
      "slotId": slotId,
      "plateNumber": plateNumber,
      "userId": userId,
      "startTime": startTime,
      "endTime": endTime,
      "createdAt": createdAt,
      "paidFee": paidFee,
      "status": status,
    };
  }

  static ReservationModel fromMap(Map<String, dynamic> data, String id) {
    return ReservationModel(
      id: id,
      slotId: data["slotId"],
      plateNumber: data["plateNumber"],
      userId: data["userId"],
      startTime: (data["startTime"] as Timestamp).toDate(),
      endTime: (data["endTime"] as Timestamp).toDate(),
      createdAt: (data["createdAt"] as Timestamp).toDate(),
      paidFee: data["paidFee"],
      status: data["status"],
    );
  }
}
