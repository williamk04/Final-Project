import React, { useEffect, useState } from "react";
import DashboardCard from "../components/DashboardCard";
import ChartRevenue from "../components/ChartRevenue";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import LocalParkingIcon from "@mui/icons-material/LocalParking";
import MonetizationOnIcon from "@mui/icons-material/MonetizationOn";
import HistoryIcon from "@mui/icons-material/History";
import { Box, Typography, CircularProgress } from "@mui/material";

import { collection, onSnapshot } from "firebase/firestore";
import { db } from "../firebaseConfig";

// Tổng số slot bãi
const TOTAL_SLOTS = 50;

// Tên các ngày trong tuần
const DAYS_OF_WEEK = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export default function Dashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    // Lắng nghe realtime collection "vehicles"
    const unsub = onSnapshot(collection(db, "vehicles"), (snapshot) => {
      const vehicles = snapshot.docs.map(doc => doc.data());

      const todayStr = new Date().toISOString().slice(0, 10);

      // Tính các chỉ số dashboard
      const todayEntries = vehicles.filter(v => v.entry_time?.startsWith(todayStr));
      const todayExits = vehicles.filter(v => v.exit_time?.startsWith(todayStr));
      const currentVehicles = vehicles.filter(v => v.status === "in");
      const revenueToday = todayExits.reduce((sum, v) => sum + (v.fee || 0), 0);
      const availableSlots = TOTAL_SLOTS - currentVehicles.length;

      // Tạo dữ liệu doanh thu tuần
      const revenueData = DAYS_OF_WEEK.map((day, i) => {
        const date = new Date();
        date.setDate(date.getDate() - (date.getDay() - i));
        const dateStr = date.toISOString().slice(0, 10);
        const exits = vehicles.filter(v => v.exit_time?.startsWith(dateStr));
        const total = exits.reduce((sum, v) => sum + (v.fee || 0), 0);
        return { day, revenue: total };
      });

      setStats({
        today_entries: todayEntries.length,
        today_exits: todayExits.length,
        current_vehicles: currentVehicles.length,
        available_slots: availableSlots,
        revenue_today: revenueToday,
        revenueData
      });
    });

    // Cleanup khi component unmount
    return () => unsub();
  }, []);

  if (!stats) {
    return (
      <Box sx={{ p: 3, display: "flex", justifyContent: "center", alignItems: "center", height: "80vh" }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
        Parking Overview (Realtime)
      </Typography>

      <Box sx={{ display: "flex", flexWrap: "wrap" }}>
        <DashboardCard title="Today's Entries" value={stats.today_entries} icon={<DirectionsCarIcon color="primary" />} />
        <DashboardCard title="Today's Exits" value={stats.today_exits} icon={<HistoryIcon color="secondary" />} />
        <DashboardCard title="Cars in Lot" value={stats.current_vehicles} icon={<DirectionsCarIcon color="success" />} />
        <DashboardCard title="Free Slots" value={stats.available_slots} icon={<LocalParkingIcon color="info" />} />
        <DashboardCard title="Today's Revenue" value={`$${stats.revenue_today}`} icon={<MonetizationOnIcon color="warning" />} />
      </Box>

      <Typography variant="h6" sx={{ mt: 4 }}>
        Weekly Revenue
      </Typography>
      <ChartRevenue data={stats.revenueData} />
    </Box>
  );
}
