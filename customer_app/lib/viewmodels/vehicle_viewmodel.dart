import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/vehicle_model.dart';
import '../models/vehicle_history_model.dart';
import '../services/vehicle_service.dart';

class VehicleViewModel extends Notifier<List<VehicleModel>> {
  final VehicleService _vehicleService = VehicleService();

  List<VehicleHistoryModel> activeSessions = [];
  List<VehicleHistoryModel> completedSessions = [];
  bool isLoading = false;

  @override
  List<VehicleModel> build() {
    _loadVehicles();
    return [];
  }

  void _loadVehicles() {
    final stream = _vehicleService.getUserVehicles();
    stream.listen((vehicles) {
      state = vehicles;
    });
  }

  /// Add a new vehicle (pending)
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

  // --- Get vehicle history ---
  Future<void> fetchVehicleHistories() async {
    isLoading = true;
    state = [...state];
    try {
      final allHistories = await _vehicleService.getVehicleHistoriesByUser();
      activeSessions = allHistories.where((v) => v.status == 'in').toList();
      completedSessions = allHistories.where((v) => v.status == 'out').toList();
    } catch (e) {
      print("Error loading vehicle histories: $e");
    } finally {
      isLoading = false;
      state = [...state];
    }
  }
}

final vehicleViewModelProvider =
    NotifierProvider<VehicleViewModel, List<VehicleModel>>(VehicleViewModel.new);
