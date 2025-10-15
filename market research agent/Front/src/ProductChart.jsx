import React, { useState, useEffect } from "react";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

const ProductChart = () => {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/api/dashboard/analytics"
        );
        const apiData = await response.json();
        const productData = apiData.mostUsedProducts;

        setChartData({
          labels: productData.map((p) => p.name),
          datasets: [
            {
              data: productData.map((p) => p.value),
              backgroundColor: [
                "#4A55A2",
                "#7895CB",
                "#A0BFE0",
                "#C5DFF8",
                "#F1EAFF",
                "#BFCCB5",
                "#E7F0DC",
                "#D2E0FB",
                "#F9F3CC",
                "#D7E5CA",
              ],
              borderWidth: 0,
            },
          ],
        });
      } catch (err) {
        console.error("Error fetching product data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { position: "bottom" } },
  };

  return (
    <div className="chart-container" style={{ height: "400px", position: "relative" }}>
      <h3>Most Used Products</h3>
      <div style={{ height: "350px", position: "relative" }}>
        {loading && (
          <div
            style={{
              height: "100%",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              fontSize: "18px",
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              color:"black",
              background: "#ffffffff",
              zIndex: 10,
            }}
          >
            Loading chart...
          </div>
        )}
        {chartData && <Pie data={chartData} options={options} />}
      </div>
    </div>
  );
};

export default ProductChart;
