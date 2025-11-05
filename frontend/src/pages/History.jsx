import React, { useEffect, useState } from "react";
import { collection, onSnapshot } from "firebase/firestore";
import { db } from "../firebaseConfig";
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  TextField,
  MenuItem
} from "@mui/material";

export default function History() {
  const [vehicles, setVehicles] = useState(null);
  const [searchText, setSearchText] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => {
    const unsub = onSnapshot(collection(db, "vehicles"), (snapshot) => {
      const data = snapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data(),
      }));
      data.sort((a, b) => new Date(b.entry_time) - new Date(a.entry_time));
      setVehicles(data);
    });

    return () => unsub();
  }, []);

  if (!vehicles) {
    return (
      <Box sx={{ p: 3, display: "flex", justifyContent: "center", alignItems: "center", height: "80vh" }}>
        <CircularProgress />
      </Box>
    );
  }

  // Filter theo searchText và status
  const filteredVehicles = vehicles.filter((v) => {
    const matchText = v.license_plate.toLowerCase().includes(searchText.toLowerCase());
    const matchStatus = statusFilter ? v.status === statusFilter : true;
    return matchText && matchStatus;
  });

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
        Vehicle History
      </Typography>

      {/* Search & Filter */}
      <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
        <TextField
          label="Search License Plate"
          variant="outlined"
          size="small"
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
        />
        <TextField
          label="Status"
          select
          size="small"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <MenuItem value="">All</MenuItem>
          <MenuItem value="in">In</MenuItem>
          <MenuItem value="out">Out</MenuItem>
        </TextField>
      </Box>

      {/* Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>License Plate</TableCell>
              <TableCell>Entry Time</TableCell>
              <TableCell>Exit Time</TableCell>
              <TableCell>Duration (min)</TableCell>
              <TableCell>Fee</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredVehicles.map((v) => (
              <TableRow key={v.id}>
                <TableCell>{v.license_plate}</TableCell>
                <TableCell>{new Date(v.entry_time).toLocaleString()}</TableCell>
                <TableCell>{v.exit_time ? new Date(v.exit_time).toLocaleString() : "-"}</TableCell>
                <TableCell>{v.duration_minutes ?? "-"}</TableCell>
                <TableCell>{v.fee ? `$${v.fee}` : "-"}</TableCell>
                <TableCell>{v.status}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
