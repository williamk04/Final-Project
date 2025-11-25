import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../models/parking_slot_model.dart';
import '../../models/reservation_model.dart';
import '../../viewmodels/reservation_viewmodel.dart';
import '../../viewmodels/vehicle_viewmodel.dart';

class ReservationPage extends ConsumerStatefulWidget {
  const ReservationPage({super.key});

  @override
  ConsumerState<ReservationPage> createState() => _ReservationPageState();
}

class _ReservationPageState extends ConsumerState<ReservationPage> {
  String? selectedPlate;
  DateTime? startTime;
  DateTime? endTime;
  int? estimatedFee;
  final df = DateFormat('HH:mm');
  static const int pricePerHour = 20000;

  Future<void> pickStartTime() async {
    final now = DateTime.now();
    final time = await showTimePicker(context: context, initialTime: TimeOfDay.now());
    if (time == null) return;

    final selected = DateTime(now.year, now.month, now.day, time.hour, time.minute);
    if (selected.isBefore(now)) {
      _showMsg("Giờ bắt đầu không được nhỏ hơn hiện tại!");
      return;
    }

    setState(() {
      startTime = selected;
      _autoLoadSlots();
      _calculateEstimatedFee();
    });
  }

  Future<void> pickEndTime() async {
    if (startTime == null) {
      _showMsg("Hãy chọn giờ bắt đầu trước!");
      return;
    }

    final now = DateTime.now();
    final time = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.fromDateTime(startTime!.add(const Duration(hours: 1))),
    );
    if (time == null) return;

    final selected = DateTime(now.year, now.month, now.day, time.hour, time.minute);
    if (selected.isBefore(startTime!)) {
      _showMsg("Giờ kết thúc phải sau giờ bắt đầu!");
      return;
    }

    setState(() {
      endTime = selected;
      _autoLoadSlots();
      _calculateEstimatedFee();
    });
  }

  void _calculateEstimatedFee() {
    if (startTime != null && endTime != null) {
      final duration = endTime!.difference(startTime!);
      final hours = (duration.inMinutes / 60).ceil();
      estimatedFee = hours * pricePerHour;
    } else {
      estimatedFee = null;
    }
  }

  void _autoLoadSlots() {
    if (startTime != null && endTime != null) {
      final vm = ref.read(reservationViewModelProvider.notifier);
      vm.startTime = startTime!;
      vm.endTime = endTime!;
      vm.loadAvailableSlots();
    }
  }

  void _showMsg(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
  }

  Future<void> _bookSlot(ParkingSlotModel slot) async {
    if (selectedPlate == null) {
      _showMsg("Hãy chọn biển số");
      return;
    }

    final vm = ref.read(reservationViewModelProvider.notifier);
    try {
      await vm.bookSlot(slot, selectedPlate!);
      _showMsg("Đặt chỗ thành công!");
      setState(() {
        startTime = null;
        endTime = null;
        selectedPlate = null;
        estimatedFee = null;
      });
    } catch (e) {
      _showMsg(e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    final vehicles = ref
        .watch(vehicleViewModelProvider)
        .where((v) => v.status == "approved")
        .toList();
    final availableSlots = ref.watch(reservationViewModelProvider);
    final reservationVM = ref.read(reservationViewModelProvider.notifier);

    return Scaffold(
      backgroundColor: const Color(0xFFF2F4F7),
      appBar: AppBar(
        title: const Text("Đặt chỗ đỗ xe", style: TextStyle(fontWeight: FontWeight.bold)),
        centerTitle: true,
        backgroundColor: Colors.blueAccent,
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _sectionTitle("Thông tin xe"),
            _infoCard(
              child: DropdownButtonFormField<String>(
                value: selectedPlate,
                decoration: const InputDecoration(border: InputBorder.none),
                hint: const Text("Chọn biển số xe"),
                items: vehicles.map((v) => DropdownMenuItem(value: v.plateNumber, child: Text(v.plateNumber))).toList(),
                onChanged: (v) {
                  setState(() {
                    selectedPlate = v;
                    _autoLoadSlots();
                  });
                },
              ),
            ),
            const SizedBox(height: 16),
            _sectionTitle("Thời gian"),
            _infoCard(
              child: Column(
                children: [
                  _timeRow(label: "Bắt đầu", value: startTime == null ? "Chọn giờ" : df.format(startTime!), onTap: pickStartTime),
                  const Divider(),
                  _timeRow(label: "Kết thúc", value: endTime == null ? "Chọn giờ" : df.format(endTime!), onTap: pickEndTime),
                ],
              ),
            ),
            if (estimatedFee != null)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: Text("Phí dự kiến: ₫$estimatedFee", style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            const SizedBox(height: 16),
            _sectionTitle("Slot khả dụng"),
            Expanded(
              flex: 2,
              child: availableSlots.isEmpty
                  ? Center(child: Text("Không có slot trống", style: TextStyle(color: Colors.grey.shade600)))
                  : ListView.builder(
                      itemCount: availableSlots.length,
                      itemBuilder: (context, index) {
                        final slot = availableSlots[index];
                        return _slotCard(slot);
                      },
                    ),
            ),
            const SizedBox(height: 16),
            _sectionTitle("My Reservations"),
            Expanded(
              flex: 3,
              child: StreamBuilder<List<ReservationModel>>(
                stream: reservationVM.getUserReservationsStream(),
                builder: (context, snapshot) {
                  if (!snapshot.hasData) {
                    return const Center(child: CircularProgressIndicator());
                  }
                  final myReservations = snapshot.data!;
                  if (myReservations.isEmpty) {
                    return Center(child: Text("Bạn chưa có reservation nào", style: TextStyle(color: Colors.grey.shade600)));
                  }
                  return ListView.builder(
                    itemCount: myReservations.length,
                    itemBuilder: (context, index) {
                      final r = myReservations[index];
                      return Card(
                        child: ListTile(
                          title: Text("Slot: ${r.slotId} - Plate: ${r.plateNumber}"),
                          subtitle: Text("${DateFormat('dd/MM HH:mm').format(r.startTime)} → "
                              "${DateFormat('dd/MM HH:mm').format(r.endTime)}\nStatus: ${r.status}"),
                          trailing: r.status == "reserved"
                              ? ElevatedButton(
                                  style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                                  onPressed: () async {
                                    await reservationVM.cancelReservation(r.id);
                                    _showMsg("Reservation đã bị hủy");
                                  },
                                  child: const Text("Cancel"),
                                )
                              : const Text("Cancelled", style: TextStyle(color: Colors.grey)),
                        ),
                      );
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _slotCard(ParkingSlotModel slot) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 6),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ListTile(
        title: Text(slot.name),
        trailing: ElevatedButton(
          style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blueAccent,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))),
          onPressed: () => _bookSlot(slot),
          child: const Text("Đặt"),
        ),
      ),
    );
  }

  Widget _sectionTitle(String text) {
    return Align(alignment: Alignment.centerLeft, child: Text(text, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600)));
  }

  Widget _infoCard({required Widget child}) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      margin: const EdgeInsets.only(top: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 8, offset: const Offset(0, 4))],
      ),
      child: child,
    );
  }

  Widget _timeRow({required String label, required String value, required VoidCallback onTap}) {
    return InkWell(
      onTap: onTap,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 16)),
          Row(
            children: [
              Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(width: 8),
              const Icon(Icons.access_time, color: Colors.blueAccent)
            ],
          )
        ],
      ),
    );
  }
}
