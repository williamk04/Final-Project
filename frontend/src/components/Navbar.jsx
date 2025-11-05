import React from "react";
import { Tabs, Tab, Box } from "@mui/material";
import { useLocation, useNavigate } from "react-router-dom";

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();

  const tabValue = location.pathname;

  return (
    <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
      <Tabs
        value={tabValue}
        onChange={(e, newValue) => navigate(newValue)}
        textColor="primary"
        indicatorColor="primary"
      >
        <Tab label="Dashboard" value="/dashboard" />
        <Tab label="History" value="/history" />
        <Tab label="Parking Map" value="/map" />
      </Tabs>
    </Box>
  );
}
