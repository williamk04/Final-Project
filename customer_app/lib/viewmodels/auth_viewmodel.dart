import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart'; // ✅ thêm dòng này
import '../services/auth_service.dart';

// Provider theo Riverpod 3.x
final authViewModelProvider = NotifierProvider<AuthViewModel, bool>(AuthViewModel.new);

class AuthViewModel extends Notifier<bool> {
  final AuthService _authService = AuthService();

  @override
  bool build() => false; // mặc định chưa loading

  Future<void> register(BuildContext context, String email, String password) async {
    try {
      state = true;
      await _authService.register(email, password);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Register success!')),
      );

      // ✅ Dùng go_router thay vì Navigator
      context.go('/login');
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    } finally {
      state = false;
    }
  }

  Future<void> login(BuildContext context, String email, String password) async {
    try {
      state = true;
      await _authService.login(email, password);

      // ✅ Điều hướng bằng go_router
      context.go('/home');
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    } finally {
      state = false;
    }
  }

  Future<void> logout(BuildContext context) async {
    await _authService.logout();

    // ✅ Quay lại trang login
    context.go('/login');
  }
}
