import axios from "axios";

const API_BASE = "http://localhost:5000/api"; 

export const getAllVehicles = async () => {
  try {
    const res = await axios.get(`${API_BASE}/vehicles`);
    return res.data;
  } catch (err) {
    console.error(err);
    return [];
  }
};
