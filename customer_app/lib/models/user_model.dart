import 'package:cloud_firestore/cloud_firestore.dart';

class UserModel {
  final String id; // uid của Firebase Auth
  final String email;
  final String? name;
  final int walletBalance;
  final int walletDebt;
  final String? fcmToken;
  final DateTime createdAt;

  UserModel({
    required this.id,
    required this.email,
    required this.name,
    required this.walletBalance,
    required this.walletDebt,
    required this.fcmToken,
    required this.createdAt,
  });

  factory UserModel.fromMap(String id, Map<String, dynamic> data) {
    return UserModel(
      id: id,
      email: data['email'] ?? '',
      name: data['name'],
      walletBalance: (data['wallet_balance'] ?? 0).toInt(),
      walletDebt: (data['wallet_debt'] ?? 0).toInt(),
      fcmToken: data['fcmToken'],
      createdAt: (data['createdAt'] is Timestamp)
          ? (data['createdAt'] as Timestamp).toDate()
          : DateTime.tryParse(data['createdAt'] ?? '') ?? DateTime.now(),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'email': email,
      'name': name,
      'wallet_balance': walletBalance,
      'wallet_debt': walletDebt,
      'fcmToken': fcmToken,
      'createdAt': createdAt,
    };
  }
}
