import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/reservation_model.dart';

class ReservationService {
  final _firestore = FirebaseFirestore.instance;

  Future<void> createReservationWithId(String id, ReservationModel model) async {
    await _firestore.collection('reservations').doc(id).set({
      ...model.toMap(),
      'startTime': Timestamp.fromDate(model.startTime),
      'endTime': Timestamp.fromDate(model.endTime),
      'createdAt': FieldValue.serverTimestamp(),
    });
  }

  Future<void> cancelReservation(String id) async {
    await _firestore.collection('reservations').doc(id).update({
      "status": "cancelled",
    });
  }

  // Stream lấy tất cả reservation của user có status = "reserved"
  Stream<List<ReservationModel>> getUserReservations(String userId) {
    return _firestore
        .collection("reservations")
        .where("userId", isEqualTo: userId)
        .where("status", isEqualTo: "reserved")
        .orderBy("createdAt", descending: true)
        .snapshots()
        .map((snap) => snap.docs
            .map((doc) => ReservationModel.fromMap(doc.data(), doc.id))
            .toList());
  }
}
