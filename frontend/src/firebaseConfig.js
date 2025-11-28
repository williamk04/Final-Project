// src/firebaseConfig.js
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getAuth } from "firebase/auth";

// ⚠️ Điền config thật của bạn trong Firebase Console
const firebaseConfig = {
  apiKey: "AIzaSyBlrUW3w3PLOx-FAer1_cJh9wNmrGR4yBk",
  authDomain: "parking-project-9830e.firebaseapp.com",
  projectId: "parking-project-9830e",
  storageBucket: "parking-project-9830e.firebasestorage.app",
  messagingSenderId: "120357076341",
  appId: "1:120357076341:web:66e9a22ff971e66ffa273c"
};

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
export const auth = getAuth(app);
