/// Modelo del perfil de usuario.
class UserProfileModel {
  final String userId;
  final String? name;
  final List<String> likes;
  final List<String> events;

  UserProfileModel({
    required this.userId,
    this.name,
    this.likes = const [],
    this.events = const [],
  });

  factory UserProfileModel.fromJson(Map<String, dynamic> json) {
    return UserProfileModel(
      userId: json['user_id'] as String,
      name: json['name'] as String?,
      likes: (json['likes'] as List<dynamic>?)?.cast<String>() ?? [],
      events: (json['events'] as List<dynamic>?)?.cast<String>() ?? [],
    );
  }
}
