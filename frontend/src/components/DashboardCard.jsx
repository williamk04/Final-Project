import React from "react";
import { Card, CardContent, Typography } from "@mui/material";

const DashboardCard = ({ title, value, icon }) => {
  return (
    <Card sx={{ flex: 1, m: 1, borderRadius: 3, boxShadow: 3 }}>
      <CardContent>
        <Typography variant="subtitle2" color="text.secondary">
          {title}
        </Typography>
        <Typography variant="h4" sx={{ mt: 1, display: "flex", alignItems: "center", gap: 1 }}>
          {icon} {value}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default DashboardCard;
