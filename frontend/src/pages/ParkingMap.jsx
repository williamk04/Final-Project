import React from "react";
import { Box, Typography } from "@mui/material";

const slots = [
  { id: "A1", status: "free" },
  { id: "A2", status: "occupied" },
  { id: "A3", status: "free" },
  { id: "A4", status: "occupied" },
  { id: "A5", status: "free" },
  { id: "A6", status: "free" },
];

const ParkingMap = () => {
  return (
    <Box
      sx={{
        p: 4,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        backgroundColor: "#f5f5f5",
        minHeight: "100vh",
      }}
    >
      <Typography
        variant="h4"
        sx={{ mb: 4, fontWeight: 700, textTransform: "uppercase", color: "#333" }}
      >
        Parking Map
      </Typography>

      <Box
        sx={{
          width: 1000,
          height: 650,
          border: "5px solid #333",
          borderRadius: 3,
          position: "relative",
          backgroundColor: "#ffffff",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          p: 3,
          boxShadow: "0 4px 20px rgba(0,0,0,0.1)",
        }}
      >
        {/* Các ô đỗ xe */}
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "repeat(6, 1fr)",
            gap: 3,
            justifyItems: "center",
            alignItems: "center",
            mt: 4,
          }}
        >
          {slots.map((slot) => (
            <Box
              key={slot.id}
              sx={{
                width: 120,
                height: 180,
                borderRadius: 2,
                border: "3px solid #555",
                backgroundColor:
                  slot.status === "free" ? "#a5d6a7" : "#ef9a9a",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                fontWeight: "bold",
                color: "#333",
                fontSize: "1.6rem",
                transition: "0.3s",
                "&:hover": {
                  transform: "scale(1.07)",
                  boxShadow: "0 0 15px rgba(0,0,0,0.3)",
                },
              }}
            >
              {slot.id}
            </Box>
          ))}
        </Box>

        {/* Lối vào / ra ở giữa cạnh dưới */}
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            gap: 10,
            mb: 2,
          }}
        >
          <Typography
            variant="h6"
            sx={{
              fontWeight: 700,
              color: "#e53935",
              border: "3px solid #e53935",
              px: 4,
              py: 1,
              borderRadius: "12px",
              backgroundColor: "#ffebee",
            }}
          >
            Exit
          </Typography>
          <Typography
            variant="h6"
            sx={{
              fontWeight: 700,
              color: "#2e7d32",
              border: "3px solid #2e7d32",
              px: 4,
              py: 1,
              borderRadius: "12px",
              backgroundColor: "#e8f5e9",
            }}
          >
            Entry
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default ParkingMap;
