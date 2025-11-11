import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../models/vehicle_model.dart';
import '../models/vehicle_history_model.dart';

class VehicleService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final FirebaseAuth _auth = FirebaseAuth.instance;

  // --- 🆕 Add a new vehicle request ---
  Future<void> addVehicle(String plateNumber, {String status = 'pending'}) async {
    final user = _auth.currentUser;
    if (user == null) throw Exception('User not logged in');

    // ✅ Check if plate already exists (approved or pending)
    final existing = await _firestore
        .collection('user_plates')
        .where('plateNumber', isEqualTo: plateNumber)
        .get();

    if (existing.docs.isNotEmpty) {
      final existingStatus = existing.docs.first['status'];
      if (existingStatus == 'approved') {
        throw Exception('This plate number has already been registered.');
      } else if (existingStatus == 'pending') {
        throw Exception('This plate number is already pending approval.');
      }
    }

    // ✅ Create a new pending request
    final docRef = _firestore.collection('user_plates').doc();
    final vehicle = VehicleModel(
      id: docRef.id,
      plateNumber: plateNumber,
      userId: user.uid,
      status: status,
    );

    await docRef.set(vehicle.toMap());
  }

  // --- Stream: vehicles of the current user ---
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

  // --- Update a vehicle plate number ---
  Future<void> updateVehicle(String id, String newPlateNumber) async {
    await _firestore.collection('user_plates').doc(id).update({
      'plateNumber': newPlateNumber,
    });
  }

  // --- Delete a vehicle ---
  Future<void> deleteVehicle(String id) async {
    await _firestore.collection('user_plates').doc(id).delete();
  }

  // --- Update vehicle status (used by admin) ---
  Future<void> updateStatus(String id, String newStatus) async {
    await _firestore.collection('user_plates').doc(id).update({
      'status': newStatus,
    });
  }

  // --- Get all pending vehicles (for admin) ---
  Stream<List<VehicleModel>> getPendingVehicles() {
    return _firestore
        .collection('user_plates')
        .where('status', isEqualTo: 'pending')
        .snapshots()
        .map((snapshot) =>
            snapshot.docs.map((doc) => VehicleModel.fromMap(doc.data())).toList());
  }

  // --- Get vehicle histories for approved vehicles ---
  Future<List<VehicleHistoryModel>> getVehicleHistoriesByUser() async {
    final user = _auth.currentUser;
    if (user == null) throw Exception('User not logged in');

    final plateSnapshot = await _firestore
        .collection('user_plates')
        .where('userId', isEqualTo: user.uid)
        .where('status', isEqualTo: 'approved')
        .get();

    final plateNumbers = plateSnapshot.docs.map((d) => d['plateNumber']).toList();
    if (plateNumbers.isEmpty) return [];

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
