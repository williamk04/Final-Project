import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../viewmodels/vehicle_viewmodel.dart';
import '../../models/vehicle_history_model.dart';

class HistoryScreen extends ConsumerStatefulWidget {
  const HistoryScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends ConsumerState<HistoryScreen> {
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // ✅ Gọi fetchVehicleHistories() sau khi widget và provider sẵn sàng
    Future.microtask(() async {
      await ref.read(vehicleViewModelProvider.notifier).fetchVehicleHistories();
    });
  }

  @override
  Widget build(BuildContext context) {
    // ✅ Watch cả state để Riverpod rebuild khi dữ liệu thay đổi
    final vehicles = ref.watch(vehicleViewModelProvider);
    final vm = ref.watch(vehicleViewModelProvider.notifier);
    final isLoading = vm.isLoading;

    return Scaffold(
      appBar: AppBar(title: const Text("Parking History")),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : (vm.activeSessions.isEmpty && vm.completedSessions.isEmpty)
              ? const Center(
                  child: Text(
                    "No history found",
                    style: TextStyle(fontSize: 16, color: Colors.grey),
                  ),
                )
              : RefreshIndicator(
                  onRefresh: () async {
                    await ref
                        .read(vehicleViewModelProvider.notifier)
                        .fetchVehicleHistories();
                  },
                  child: SingleChildScrollView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          "Active Session",
                          style: TextStyle(
                              fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        if (vm.activeSessions.isEmpty)
                          const Text("No active sessions",
                              style: TextStyle(color: Colors.grey))
                        else
                          ...vm.activeSessions
                              .map((v) => _buildSessionCard(v, true)),

                        const SizedBox(height: 20),
                        const Text(
                          "Completed Sessions",
                          style: TextStyle(
                              fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        if (vm.completedSessions.isEmpty)
                          const Text("No completed sessions",
                              style: TextStyle(color: Colors.grey))
                        else
                          ...vm.completedSessions
                              .map((v) => _buildSessionCard(v, false)),
                      ],
                    ),
                  ),
                ),
    );
  }

  Widget _buildSessionCard(VehicleHistoryModel v, bool isActive) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: Image.network(
            v.imageUrl,
            width: 60,
            height: 60,
            fit: BoxFit.cover,
            errorBuilder: (_, __, ___) =>
                const Icon(Icons.image_not_supported, size: 60),
          ),
        ),
        title: Text(
          v.licensePlate,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(
          isActive
              ? "Entry: ${v.entryTime}\nStatus: Active"
              : "Exit: ${v.exitTime}\nFee: \$${v.fee ?? 0}\nDuration: ${v.durationMinutes} min",
        ),
        trailing: isActive
            ? const Text(
                "\$40/hr",
                style: TextStyle(
                  color: Colors.blue,
                  fontWeight: FontWeight.bold,
                ),
              )
            : const Icon(Icons.check_circle, color: Colors.green),
      ),
    );
  }
}
