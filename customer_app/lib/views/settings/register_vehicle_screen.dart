import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../viewmodels/vehicle_viewmodel.dart';
import '../../models/vehicle_model.dart';

class RegisterVehicleScreen extends ConsumerWidget {
  const RegisterVehicleScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final vehicleList = ref.watch(vehicleViewModelProvider);
    final vehicleVM = ref.read(vehicleViewModelProvider.notifier);
    final plateController = TextEditingController();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Register Vehicle'),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text(
              "Add Your Vehicle Plate",
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),

            // Ô nhập biển số xe
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: plateController,
                    inputFormatters: [
                      UpperCaseTextFormatter(), // ✅ luôn viết hoa
                    ],
                    decoration: InputDecoration(
                      labelText: 'Enter license plate',
                      prefixIcon: const Icon(Icons.directions_car),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                ElevatedButton(
                  onPressed: () async {
                    final plate = plateController.text.trim();
                    if (plate.isEmpty) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text("Please enter plate number"),
                          behavior: SnackBarBehavior.floating,
                        ),
                      );
                      return;
                    }

                    await vehicleVM.addVehicle(plate);
                    plateController.clear();

                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text("Vehicle added successfully!"),
                        behavior: SnackBarBehavior.floating,
                      ),
                    );
                  },
                  child: const Text("Add"),
                ),
              ],
            ),

            const SizedBox(height: 20),
            const Divider(),
            const SizedBox(height: 10),
            const Text(
              "Registered Vehicles",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 10),

            // Danh sách biển số đã đăng ký
            Expanded(
              child: vehicleList.isEmpty
                  ? const Center(child: Text("No vehicles registered yet."))
                  : ListView.builder(
                      itemCount: vehicleList.length,
                      itemBuilder: (context, index) {
                        final v = vehicleList[index];
                        return Card(
                          margin: const EdgeInsets.symmetric(vertical: 6),
                          child: ListTile(
                            leading: const Icon(Icons.local_taxi,
                                color: Colors.blueAccent),
                            title: Text(
                              v.plateNumber,
                              style: const TextStyle(fontSize: 16),
                            ),
                            trailing: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                IconButton(
                                  icon: const Icon(Icons.edit,
                                      color: Colors.orange),
                                  onPressed: () {
                                    _showEditDialog(context, vehicleVM, v);
                                  },
                                ),
                                IconButton(
                                  icon: const Icon(Icons.delete,
                                      color: Colors.red),
                                  onPressed: () {
                                    _confirmDelete(context, vehicleVM, v.id!);
                                  },
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }

  // ✏️ Hộp thoại sửa biển số
  void _showEditDialog(
      BuildContext context, VehicleViewModel vm, VehicleModel vehicle) {
    final controller = TextEditingController(text: vehicle.plateNumber);

    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text("Edit Plate Number"),
        content: TextField(
          controller: controller,
          inputFormatters: [UpperCaseTextFormatter()],
          decoration: const InputDecoration(labelText: "New plate number"),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("Cancel"),
          ),
          ElevatedButton(
            onPressed: () async {
              final newPlate = controller.text.trim();
              if (newPlate.isEmpty) return;

              Navigator.pop(context); // đóng dialog trước khi update
              await vm.updateVehicle(vehicle.id!, newPlate);

              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text("Vehicle updated successfully!"),
                  behavior: SnackBarBehavior.floating,
                ),
              );
            },
            child: const Text("Save"),
          ),
        ],
      ),
    );
  }

  // ❌ Hộp thoại xác nhận xóa
  void _confirmDelete(BuildContext context, VehicleViewModel vm, String id) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text("Delete Vehicle"),
        content: const Text("Are you sure you want to delete this plate?"),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("Cancel"),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () async {
              Navigator.pop(context); // đóng dialog trước
              await vm.deleteVehicle(id);

              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text("Vehicle deleted successfully!"),
                  behavior: SnackBarBehavior.floating,
                ),
              );
            },
            child: const Text("Delete"),
          ),
        ],
      ),
    );
  }
}

// 🔠 Formatter giúp auto UPPERCASE
class UpperCaseTextFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    return newValue.copyWith(
      text: newValue.text.toUpperCase(),
      selection: newValue.selection,
    );
  }
}
