import React, { useState, useEffect } from "react";
import { Radar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const Dimensions = [
  "Usability",
  "Features",
  "Innovation",
  "Integration",
  "Onboarding",
];

const SpiderChart = () => {
  const [chartData, setChartData] = useState({ datasets: [] });
  const [productName, setProductName] = useState("Product A");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          "http://127.0.0.1:8000/api/dashboard/analytics"
        );
        const apiData = await response.json();

        const SpiderChart = apiData.SpiderChart; // assuming backend provides this
        setChartData({
          labels: Dimensions,
          datasets: [
            {
              label: SpiderChart.productName,
              data: SpiderChart.scores,
              backgroundColor: "rgba(88, 88, 117, 0.2)",
              borderColor: "#000000",
              pointBackgroundColor: "#000000",
              pointBorderColor: "#000000",
              borderWidth: 2,
            },
          ],
        });
      } catch (error) {
        console.error("Failed to fetch spider chart data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [productName]);

  const options = {
    scales: {
      r: {
        min: 0,
        max: 5,
        ticks: { stepSize: 1, color: "#000000", backdropColor: "transparent" },
        grid: { color: "rgba(0, 0, 0, 0.3)" },
        angleLines: { color: "rgba(0, 0, 0, 0.3)" },
        pointLabels: { color: "#000000", font: { size: 14 } },
      },
    },
    responsive: true,
    plugins: {
      legend: { position: "top", labels: { color: "#000000" } },
      tooltip: { enabled: true },
    },
  };

  if (loading) {
    return (
      <div
        style={{
          width: "500px",
          height: "400px",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          margin: "0 auto",
        }}
      >
        <span style={{ color: "#000000", fontSize: "18px" }}>
          Loading Insights...
        </span>
      </div>
    );
  }

  return (
    <div style={{ width: "500px", margin: "0 auto", textAlign: "center" }}>
      <h2 style={{ color: "#000000", marginBottom: "10px" }}>
         Insights
      </h2>
      <Radar data={chartData} options={options} />
    </div>
  );
};

export default SpiderChart;
