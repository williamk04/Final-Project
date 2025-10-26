import React from "react";
import { Routes, Route } from "react-router-dom";
import Dashboard from "../pages/Dashboard/Dashboard";
import VehicleHistory from "../pages/VehicleHistory/VehicleHistory";

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/history" element={<VehicleHistory />} />
    </Routes>
  );
};

export default AppRoutes;
