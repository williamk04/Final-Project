import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../models/vehicle_model.dart';
import '../models/vehicle_history_model.dart';
import '../models/reservation_model.dart';
import '../services/vehicle_service.dart';
import '../services/reservation_service.dart';

class VehicleViewModel extends Notifier<List<VehicleModel>> {
  final VehicleService _vehicleService = VehicleService();
  final ReservationService _reservationService = ReservationService();

  List<VehicleHistoryModel> activeSessions = [];
  List<VehicleHistoryModel> completedSessions = [];

  /// 🆕 approved plates
  List<VehicleModel> approvedPlates = [];

  /// 🆕 reservations của user
  List<ReservationModel> myReservations = [];

  bool isLoading = false;

  @override
  List<VehicleModel> build() {
    _loadVehicles();
    _loadApprovedPlates();
    _loadMyReservations(); // load reservations
    return [];
  }

  void _loadVehicles() {
    _vehicleService.getUserVehicles().listen((vehicles) {
      state = vehicles;
    });
  }

  void _loadApprovedPlates() {
    _vehicleService.getApprovedPlates().listen((plates) {
      approvedPlates = plates;
      state = [...state]; // refresh UI
    });
  }

  /// 🆕 Load reservations stream của user
  void _loadMyReservations() {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) return;

    _reservationService.getUserReservations(user.uid).listen((list) {
      myReservations = list;
      state = [...state]; // refresh UI
    });
  }

  Future<void> addVehicle(String plateNumber) async {
    await _vehicleService.addVehicle(plateNumber, status: 'pending');
  }

  Future<void> updateVehicle(String id, String newPlateNumber) async {
    await _vehicleService.updateVehicle(id, newPlateNumber);
  }

  Future<void> deleteVehicle(String id) async {
    await _vehicleService.deleteVehicle(id);
  }

  Future<void> updateStatus(String id, String newStatus) async {
    await _vehicleService.updateStatus(id, newStatus);
  }

  Future<void> fetchVehicleHistories() async {
    isLoading = true;
    state = [...state];
    try {
      final allHistories = await _vehicleService.getVehicleHistoriesByUser();
      activeSessions = allHistories.where((v) => v.status == 'in').toList();
      completedSessions = allHistories.where((v) => v.status == 'out').toList();
    } finally {
      isLoading = false;
      state = [...state];
    }
  }

  /// 🆕 Hủy reservation
  Future<void> cancelReservation(String reservationId) async {
    await _reservationService.cancelReservation(reservationId);
  }
}

final vehicleViewModelProvider =
    NotifierProvider<VehicleViewModel, List<VehicleModel>>(VehicleViewModel.new);
