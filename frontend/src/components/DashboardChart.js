
import { Bar, Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

export const VehicleBarChart = ({ labels, inData, outData }) => {
  const data = {
    labels,
    datasets: [
      {
        label: "Car in",
        data: inData,
        backgroundColor: "rgba(23, 162, 184, 0.7)"
      },
      {
        label: "Car out",
        data: outData,
        backgroundColor: "rgba(40, 167, 69, 0.7)"
      }
    ]
  };

  return <Bar data={data} options={{ responsive: true }} />;
};

export const VehiclePieChart = ({ inCount, outCount }) => {
  const data = {
    labels: ["car has entered", "car has exited"],
    datasets: [
      {
        label: "The percentage of car",
        data: [inCount, outCount],
        backgroundColor: ["#17a2b8", "#28a745"]
      }
    ]
  };

  return <Pie data={data} options={{ responsive: true }} />;
};
