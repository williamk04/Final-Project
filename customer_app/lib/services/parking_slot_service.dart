import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/parking_slot_model.dart';

class ParkingSlotService {
  final _firestore = FirebaseFirestore.instance;

  Stream<List<ParkingSlotModel>> getActiveSlots() {
    return _firestore
        .collection("parking_slots")
        .where("isActive", isEqualTo: true)
        .snapshots()
        .map((snap) => snap.docs
            .map((d) => ParkingSlotModel.fromMap(d.data(), d.id))
            .toList());
  }

  /// Lấy danh sách reservation bận trong khoảng thời gian
  Future<List<Map<String, dynamic>>> getBusyReservations(
      DateTime start, DateTime end) async {
    final res = await _firestore
        .collection("reservations")
        .where("status", whereIn: ["reserved", "checked_in"])
        .get();

    // Filter trong Dart: start < endReservation && end > startReservation
    return res.docs.map((d) => d.data()..['id'] = d.id).where((r) {
      final rStart = (r['startTime'] as Timestamp).toDate();
      final rEnd = (r['endTime'] as Timestamp).toDate();
      return start.isBefore(rEnd) && end.isAfter(rStart);
    }).toList();
  }
}
