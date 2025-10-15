import React, { useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const SentimentChart = () => {
  const [chartData, setChartData] = useState({ datasets: [] });
  const [loading, setLoading] = useState(true); // loading state

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/api/dashboard/analytics"
        );
        const apiData = await response.json();
        const sentimentData = apiData.sentimentAnalysis;

        const backgroundColors = [
          "rgba(54, 162, 235, 0.2)",
          "rgba(255, 99, 132, 0.2)",
        ];
        const borderColors = ["rgb(54, 162, 235)", "rgb(255, 99, 132)"];

        setChartData({
          labels: sentimentData.labels,
          datasets: sentimentData.datasets.map((dataset, index) => ({
            ...dataset,
            fill: true,
            backgroundColor: backgroundColors[index],
            borderColor: borderColors[index],
            tension: 0.4,
          })),
        });
      } catch (error) {
        console.error("Error fetching sentiment data:", error);
      } finally {
        setLoading(false); // stop loading after fetch
      }
    };

    fetchData();
  }, []);

  const options = {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true } },
  };

  // Loading overlay style
  if (loading) {
    return (
      <div
        style={{
          height: "100%",
          borderRadius:"10px",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          fontSize: "18px",
          backgroundColor:"white",
          color: "#000000ff",
        }}
      >
        Loading Sentiment Chart...
      </div>
    );
  }

  return (
    <div className="chart-container">
      <h3>Sentiment Analysis</h3>
      <Line data={chartData} options={options} />
    </div>
  );
};

export default SentimentChart;
