import React, { useState, useEffect } from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip);

const DurationChart = () => {
  // 1. State to hold chart data fetched from the API
  const [chartData, setChartData] = useState({
    datasets: [], // Start with an empty datasets array
  });

  // 2. useEffect to fetch data when the component mounts
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch the full JSON object from your FastAPI endpoint
        const response = await fetch(
          "http://127.0.0.1:8000/api/dashboard/analytics"
        );
        const apiData = await response.json();

        // 3. Extract the specific part of the JSON for this chart
        const durationDistribution = apiData.interviewDurationDistribution;

        // 4. Set the state with the extracted data
        setChartData({
          labels: durationDistribution.labels,
          datasets: [
            {
              data: durationDistribution.data,
              backgroundColor: "#4A55A2",
              borderRadius: 5,
            },
          ],
        });
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []); // The empty array [] ensures this effect runs only once

  const options = {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { display: false } },
      y: { grid: { display: false } },
    },
  };

  return (
    <div className="chart-container">
      <h3>Interview Duration Distribution</h3>
      {/* 5. Use the state variable 'chartData' here */}
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default DurationChart;
