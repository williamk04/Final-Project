import React, { useEffect, useState } from "react";
import { getAllVehicles } from "../../services/vehicleService";
import "bootstrap/dist/css/bootstrap.min.css";

const VehicleHistory = () => {
  const [vehicles, setVehicles] = useState([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await getAllVehicles();
        const data = Array.isArray(res) ? res : res.vehicles || [];
        setVehicles(data);
      } catch (error) {
        console.error("Error fetching vehicles:", error);
      }
    };
    fetchData();
  }, []);

  const filteredVehicles = vehicles.filter((v) =>
    v.license_plate?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="container mt-5">
      <div className="card shadow-lg border-0 rounded-4">
        <div className="card-header bg-primary text-white d-flex justify-content-between align-items-center py-3">
          <h4 className="mb-0 fw-bold">Vehicle History</h4>
          <div className="d-flex align-items-center">
            <input
              type="text"
              className="form-control form-control-sm me-2"
              placeholder="Search by license plate..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ width: "250px" }}
            />
            <button className="btn btn-light btn-sm">
              <i className="bi bi-search"></i>
            </button>
          </div>
        </div>

        <div className="card-body p-0">
          <div className="table-responsive">
            <table className="table table-hover align-middle mb-0">
              <thead className="table-light text-secondary">
                <tr>
                  <th scope="col">ID</th>
                  <th scope="col">License Plate</th>
                  <th scope="col">Image</th>
                  <th scope="col">Entry Time</th>
                  <th scope="col">Exit Time</th>
                  <th scope="col">Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredVehicles.length > 0 ? (
                  filteredVehicles.map((v, index) => (
                    <tr key={v._id}>
                      <td>{index + 1}</td>
                      <td className="fw-semibold text-dark">{v.license_plate}</td>
                      <img
                    src={v.image_url}       // image_url = "/uploads/plate_car1.jpg"
                    alt="vehicle"
                    width="120"
                    className="img-thumbnail"
                  />

                      <td>
                        {v.entry_time
                          ? new Date(v.entry_time).toLocaleString()
                          : "—"}
                      </td>
                      <td>
                        {v.exit_time
                          ? new Date(v.exit_time).toLocaleString()
                          : "—"}
                      </td>
                      <td>
                        <span
                          className={`badge rounded-pill px-3 py-2 ${
                            v.status === "in"
                              ? "bg-success-subtle text-success border border-success"
                              : "bg-danger-subtle text-danger border border-danger"
                          }`}
                        >
                          {v.status === "in" ? "In Parking" : "Exited"}
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" className="text-center text-muted py-5 fst-italic">
                      No vehicle records found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card-footer text-center text-muted small py-3">
          Showing {filteredVehicles.length} record(s)
        </div>
      </div>
    </div>
  );
};

export default VehicleHistory;
