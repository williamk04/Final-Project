import 'package:customer_app/views/home/reservation_page.dart';
import 'package:flutter/material.dart';
import '../settings/settings_screen.dart';
import '../history/history_screen.dart';
import '../balance/balance_page.dart'; // <-- import BalancePage

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  // Thêm BalancePage vào danh sách pages để khớp với 4 BottomNavigationBarItem
  final List<Widget> _pages = [
    const ReservationPage(),
    const HistoryScreen(),
    const SettingsScreen(),
    const BalancePage(), // <- đây là trang Balance
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Dùng IndexedStack giữ trạng thái từng trang khi chuyển tab
      body: IndexedStack(
        index: _selectedIndex,
        children: _pages,
      ),
      bottomNavigationBar: BottomNavigationBar(
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.history), label: 'History'),
          BottomNavigationBarItem(icon: Icon(Icons.settings), label: 'Settings'),
          BottomNavigationBarItem(
              icon: Icon(Icons.account_balance_wallet), label: 'Balance'),
        ],
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        type: BottomNavigationBarType.fixed,
      ),
    );
  }
}
