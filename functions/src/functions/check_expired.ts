import * as admin from "firebase-admin";
admin.initializeApp();

export async function updateExpiredReservations() {
  const db = admin.firestore();
  const now = new Date();

  try {
    const snapshot = await db.collection("reservations")
      .where("status", "==", "reserved")
      .get();

    const batch = db.batch();
    snapshot.forEach(doc => {
      const data = doc.data();
      const endTime = data.endTime.toDate ? data.endTime.toDate() : new Date(data.endTime);
      if (endTime < now) {
        batch.update(doc.ref, { status: "expired" });
      }
    });

    if (!snapshot.empty) {
      await batch.commit();
      console.log(`Updated ${snapshot.size} expired reservations`);
    }
  } catch (err) {
    console.error("Error updating expired reservations:", err);
  }
}
