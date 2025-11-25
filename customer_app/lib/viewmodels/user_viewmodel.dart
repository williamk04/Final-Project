import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user_model.dart';
import '../services/user_service.dart';

class UserViewModel extends Notifier<UserModel?> {
  final _service = UserService();

  @override
  UserModel? build() {
    _service.watchUserProfile().listen((data) {
      state = data;
    });
    return null;
  }
}

final userViewModelProvider =
    NotifierProvider<UserViewModel, UserModel?>(UserViewModel.new);
