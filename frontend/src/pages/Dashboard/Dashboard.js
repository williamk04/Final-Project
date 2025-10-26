import React, { useEffect, useState } from "react";
import CardStat from "../../components/CardStat";
import { getAllVehicles } from "../../services/vehicleService";
import { Row, Col, Table } from "react-bootstrap";
import { VehicleBarChart, VehiclePieChart } from "../../components/DashboardChart";

const TOTAL_SPOTS = 50;
const N_DAYS = 7;

const Dashboard = () => {
  const [vehicles, setVehicles] = useState([]);
  const [chartLabels, setChartLabels] = useState([]);
  const [inData, setInData] = useState([]);
  const [outData, setOutData] = useState([]);
  const [monthIn, setMonthIn] = useState(0);
  const [monthOut, setMonthOut] = useState(0);
  const [totalRevenueToday, setTotalRevenueToday] = useState(0);

  useEffect(() => {
    const fetchVehicles = async () => {
      try {
        const res = await getAllVehicles();
        const allVehicles = res.vehicles || [];

        setVehicles(allVehicles);

        // 7 ngày gần nhất cho biểu đồ
        const today = new Date();
        const recentDays = [];
        for (let i = N_DAYS + 1; i >= 0; i--) {
          const d = new Date(today);
          d.setDate(today.getDate() - i);
          recentDays.push(d.toLocaleDateString("sv-SE"));
        }
        setChartLabels(recentDays);

        // --- Gom nhóm xe vào/ra theo ngày ---
        const grouped = {};
        recentDays.forEach((day) => (grouped[day] = { in: 0, out: 0 }));
        allVehicles.forEach((v) => {
          const enterDay = new Date(v.entry_time).toLocaleDateString("sv-SE");
          if (grouped[enterDay]) grouped[enterDay].in += 1;

          if (v.exit_time) {
            const exitDay = new Date(v.exit_time).toLocaleDateString("sv-SE");
            if (grouped[exitDay]) grouped[exitDay].out += 1;
          }
        });
        setInData(recentDays.map((d) => grouped[d].in));
        setOutData(recentDays.map((d) => grouped[d].out));

        // --- Xe vào/ra trong tháng ---
        const now = new Date();
        const currentMonth = now.getMonth();
        const currentYear = now.getFullYear();
        let monthInCount = 0;
        let monthOutCount = 0;

        allVehicles.forEach((v) => {
          const entry = new Date(v.entry_time);
          if (entry.getMonth() === currentMonth && entry.getFullYear() === currentYear)
            monthInCount += 1;

          if (v.exit_time) {
            const exit = new Date(v.exit_time);
            if (exit.getMonth() === currentMonth && exit.getFullYear() === currentYear)
              monthOutCount += 1;
          }
        });

        setMonthIn(monthInCount);
        setMonthOut(monthOutCount);

        // Tổng doanh thu hôm nay từ revenueByDay
        const todayStr = today.toISOString().split("T")[0]; // "YYYY-MM-DD"
        const revenueToday = res.revenueByDay?.[todayStr] || 0;
        setTotalRevenueToday(revenueToday);

      } catch (err) {
        console.error("Fetch vehicles error:", err);
      }
    };

    fetchVehicles();
  }, []);

  const vehiclesIn = vehicles.filter((v) => v.status === "in").length;
  const emptySpots = TOTAL_SPOTS - vehiclesIn;

  return (
    <div>
      <h2 className="mb-4">Dashboard</h2>

      {/* --- Thống kê nhanh --- */}
      <Row>
        <Col md={3}>
          <CardStat title="car in the parking lot" value={vehiclesIn} color="#17a2b8" />
        </Col>
        <Col md={3}>
          <CardStat title="Total of car entered" value={monthIn} color="#28a745" />
        </Col>
        <Col md={3}>
          <CardStat title="Total of car exited" value={monthOut} color="#dc3545" />
        </Col>
        <Col md={3}>
          <CardStat title="Slot" value={emptySpots} color="#ffc107" />
        </Col>
      </Row>

      {/* --- Doanh thu hôm nay --- */}
      <Row className="mt-4">
        <Col md={6}>
          <CardStat
            title="Revenue today"
            value={`${totalRevenueToday.toLocaleString()} ₫`}
            color="#6610f2"
          />
        </Col>
      </Row>

      {/* --- Biểu đồ --- */}
      <Row className="mt-4">
        <Col md={8}>
          <h5>Vehicles entering/exiting by day (last 7 days)</h5>
          <VehicleBarChart labels={chartLabels} inData={inData} outData={outData} />
        </Col>
        <Col md={4}>
          <h5>Vehicle entry/exit rate this month</h5>
          <VehiclePieChart inCount={monthIn} outCount={monthOut} />
        </Col>
      </Row>

      {/* --- Bảng chi tiết --- */}
      <div className="mt-5">
        <h5>Vehicle details</h5>
        <div className="table-responsive">
          <Table striped bordered hover>
            <thead>
              <tr>
                <th>ID</th>
                <th>Plate</th>
                <th>Image in</th>
                <th>Image out</th>
                <th>Time entry</th>
                <th>Time exit</th>
                <th>Duration (minute)</th>
                <th>Fee (₫)</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {vehicles.length > 0 ? (
                vehicles.map((v, i) => (
                  <tr key={v._id}>
                    <td>{i + 1}</td>
                    <td>{v.license_plate}</td>
                    <td>
                      {v.image_url ? (
                        <img
                          
                        />
                      ) : (
                        "—"
                      )}
                    </td>
                    <td>
                      {v.exit_image_url ? (
                        <img
                          
                        />
                      ) : (
                        "—"
                      )}
                    </td>
                    <td>{v.entry_time ? new Date(v.entry_time).toLocaleString() : "—"}</td>
                    <td>{v.exit_time ? new Date(v.exit_time).toLocaleString() : "—"}</td>
                    <td>{v.duration_minutes ? v.duration_minutes.toFixed(1) : "—"}</td>
                    <td>{v.fee ? v.fee.toLocaleString() : "—"}</td>
                    <td>
                      <span
                        className={`badge ${v.status === "in" ? "bg-success" : "bg-danger"}`}
                      >
                        {v.status === "in" ? "Parking" : "Left the parking lot"}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="9" className="text-center text-muted py-4">
                    No vehicle data available.
                  </td>
                </tr>
              )}
            </tbody>
          </Table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
