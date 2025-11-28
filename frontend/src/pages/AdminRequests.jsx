import { useEffect, useState } from "react";
import { collection, query, where, onSnapshot, updateDoc, doc } from "firebase/firestore";
import { db } from "../firebaseConfig";

export default function AdminRequests() {
  const [requests, setRequests] = useState([]);

  useEffect(() => {
    const q = query(collection(db, "user_plates"), where("status", "==", "pending"));
    const unsubscribe = onSnapshot(q, (snapshot) => {
      const data = snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
      setRequests(data);
    });
    return unsubscribe;
  }, []);

  const handleApprove = async (id) => {
    await updateDoc(doc(db, "user_plates", id), { status: "approved" });
    alert("Approved successfully");
  };

  const handleReject = async (id) => {
    await updateDoc(doc(db, "user_plates", id), { status: "rejected" });
    alert("Rejected successfully");
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Pending Vehicle Registration Requests</h2>
      {requests.length === 0 ? (
        <p>No pending requests</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {requests.map((req) => (
            <li
              key={req.id}
              style={{
                background: "#f8f9fa",
                padding: "12px 16px",
                marginBottom: 10,
                borderRadius: 8,
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <strong>{req.plateNumber}</strong>
                <p style={{ margin: 0, color: "#666" }}>User: {req.userId}</p>
              </div>
              <div>
                <button
                  onClick={() => handleApprove(req.id)}
                  style={{ marginRight: 10, background: "#28a745", color: "#fff", border: "none", padding: "6px 10px", borderRadius: 6 }}
                >
                  Approve
                </button>
                <button
                  onClick={() => handleReject(req.id)}
                  style={{ background: "#dc3545", color: "#fff", border: "none", padding: "6px 10px", borderRadius: 6 }}
                >
                  Reject
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
