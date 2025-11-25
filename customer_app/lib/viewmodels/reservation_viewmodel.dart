import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/reservation_model.dart';
import '../models/parking_slot_model.dart';
import '../services/reservation_service.dart';
import '../services/parking_slot_service.dart';

class ReservationViewModel extends Notifier<List<ParkingSlotModel>> {
  final parkingService = ParkingSlotService();
  final reservationService = ReservationService();

  DateTime? startTime;
  DateTime? endTime;

  // Danh sách reservation của user (chỉ reserved)
  List<ReservationModel> myReservations = [];

  @override
  List<ParkingSlotModel> build() {
    return [];
  }

  // 🔹 Load slot khả dụng dựa trên startTime và endTime
  Future<void> loadAvailableSlots() async {
    if (startTime == null || endTime == null) return;

    try {
      final activeSlotsSnapshot = await FirebaseFirestore.instance
          .collection("parking_slots")
          .where("isActive", isEqualTo: true)
          .get();

      final activeSlots = activeSlotsSnapshot.docs
          .map((d) => ParkingSlotModel.fromMap(d.data(), d.id))
          .toList();

      // Lấy reservation đang bận
      final busyReservations =
          await parkingService.getBusyReservations(startTime!, endTime!);

      final busySlotIds = busyReservations
          .map((r) => r['slotId'] as String)
          .toSet();

      // Loại bỏ các slot bận
      state = activeSlots.where((s) => !busySlotIds.contains(s.id)).toList();
    } catch (e) {
      print("Error loading available slots: $e");
      state = [];
    }
  }

  // 🔹 Book slot
  Future<void> bookSlot(ParkingSlotModel slot, String plateNumber) async {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) throw Exception('User not logged in');
    if (startTime == null || endTime == null) {
      throw Exception('Start time or end time is null');
    }

    const int pricePerHour = 20000;
    final duration = endTime!.difference(startTime!);
    final hours = (duration.inMinutes / 60).ceil();
    final int cost = hours * pricePerHour;

    final userRef =
        FirebaseFirestore.instance.collection('users').doc(user.uid);
    final userSnap = await userRef.get();
    final walletBalance = userSnap.data()?['wallet_balance'] ?? 0;

    if (walletBalance < cost) {
      throw Exception("Số dư ví không đủ để đặt chỗ");
    }

    await userRef.update({'wallet_balance': walletBalance - cost});

    final docRef = FirebaseFirestore.instance.collection('reservations').doc();
    final model = ReservationModel(
      id: docRef.id,
      slotId: slot.id,
      plateNumber: plateNumber,
      userId: user.uid,
      startTime: startTime!,
      endTime: endTime!,
      createdAt: DateTime.now(),
      paidFee: cost,
      status: "reserved",
    );

    await reservationService.createReservationWithId(docRef.id, model);

    await loadAvailableSlots();
  }

  // 🔹 Load reservation của user bằng Stream
  Stream<List<ReservationModel>> getUserReservationsStream() {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) return const Stream.empty();

    return reservationService.getUserReservations(user.uid);
  }

  // 🔹 Cancel reservation
  Future<void> cancelReservation(String reservationId) async {
    await reservationService.cancelReservation(reservationId);
    if (startTime != null && endTime != null) {
      await loadAvailableSlots();
    }
  }
}

// 🔹 Provider
final reservationViewModelProvider =
    NotifierProvider<ReservationViewModel, List<ParkingSlotModel>>(
        ReservationViewModel.new);
