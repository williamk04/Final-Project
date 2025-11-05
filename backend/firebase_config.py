import firebase_admin
from firebase_admin import credentials, firestore

# Đường dẫn chính xác tới file JSON của bạn
cred = credentials.Certificate("parking-project-9830e-firebase-adminsdk-fbsvc-71b9b93d83.json")

# Khởi tạo Firebase App (chỉ 1 lần duy nhất)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Lấy client Firestore
db = firestore.client()
