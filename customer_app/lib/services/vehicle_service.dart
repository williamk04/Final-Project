import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../models/vehicle_model.dart';
import '../models/vehicle_history_model.dart';

class VehicleService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final FirebaseAuth _auth = FirebaseAuth.instance;

  // --- Giữ nguyên phần CRUD vehicle ---
  Future<void> addVehicle(String plateNumber) async {
    final user = _auth.currentUser;
    if (user == null) throw Exception('User not logged in');

    final docRef = _firestore.collection('user_plates').doc();
    final vehicle = VehicleModel(
      id: docRef.id,
      plateNumber: plateNumber,
      userId: user.uid,
    );

    await docRef.set(vehicle.toMap());
  }

  Stream<List<VehicleModel>> getUserVehicles() {
    final user = _auth.currentUser;
    if (user == null) throw Exception('User not logged in');

    return _firestore
        .collection('user_plates')
        .where('userId', isEqualTo: user.uid)
        .snapshots()
        .map((snapshot) =>
            snapshot.docs.map((doc) => VehicleModel.fromMap(doc.data())).toList());
  }

  Future<void> updateVehicle(String id, String newPlateNumber) async {
    await _firestore.collection('user_plates').doc(id).update({
      'plateNumber': newPlateNumber,
    });
  }

  Future<void> deleteVehicle(String id) async {
    await _firestore.collection('user_plates').doc(id).delete();
  }

  // --- 🆕 Phần mới: Lấy lịch sử xe từ collection "vehicles" ---
  Future<List<VehicleHistoryModel>> getVehicleHistoriesByUser() async {
    final user = _auth.currentUser;
    if (user == null) throw Exception('User not logged in');

    // Lấy danh sách biển số của user từ "user_plates"
    final plateSnapshot = await _firestore
        .collection('user_plates')
        .where('userId', isEqualTo: user.uid)
        .get();

    final plateNumbers = plateSnapshot.docs.map((d) => d['plateNumber']).toList();
    if (plateNumbers.isEmpty) return [];

    // Lấy danh sách lịch sử xe tương ứng
    final vehiclesSnapshot = await _firestore
        .collection('vehicles')
        .where('license_plate', whereIn: plateNumbers)
        .orderBy('entry_time', descending: true)
        .get();

    return vehiclesSnapshot.docs
        .map((doc) => VehicleHistoryModel.fromMap(doc.data()))
        .toList();
  }
}
