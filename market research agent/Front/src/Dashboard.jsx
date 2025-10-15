import React, { useState, useEffect } from "react";
import StatCard from "./StatCard";
import SentimentChart from "./SentimentChart";
import DurationChart from "./DurationChart";
import ProductChart from "./ProductChart";
import SpiderChart from "./SpiderChart";
import { LuUsers, LuSmile, LuClock, LuTrendingUp } from "react-icons/lu";
import "./dashboard.css";

const Dashboard = ({ onLogout }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/dashboard/analytics");

        if (!response.ok) {
          throw new Error("Failed to fetch dashboard data");
        }

        const apiData = await response.json();

        if (!apiData || !apiData.summaryMetrics) {
          throw new Error("Invalid dashboard data");
        }

        setDashboardData(apiData);
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
        setError(true);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100vw",
          height: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          backgroundColor: "#ffffff",
          zIndex: 9999,
          flexDirection: "column",
        }}
      >
        <div className="spinner"></div>
        <p style={{ marginTop: "10px", color: "#000000", fontSize: "18px" }}>
          Loading Dashboard...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100vw",
          height: "100vh",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          backgroundColor: "#ffffff",
          color: "#000",
          zIndex: 9999,
        }}
      >
        <h2 style={{ marginBottom: "20px" }}>❌ Failed to load dashboard</h2>
        <button
          onClick={onLogout}
          style={{
            background: "#000",
            color: "#fff",
            padding: "10px 20px",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontSize: "16px",
          }}
        >
          Logout
        </button>
      </div>
    );
  }

  if (!dashboardData) {
    return null;
  }

  const formatTrend = (change) => `${change > 0 ? "+" : ""}${change}%`;
  const { summaryMetrics, lastUpdated } = dashboardData;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Analytics Dashboard</h1>
        <p className="last-updated">
          Last updated: {new Date(lastUpdated).toLocaleString()}
        </p>
        <button onClick={onLogout} className="logout-button">
          Logout
        </button>
      </header>

      <div className="dashboard-grid">
        <StatCard
          title="Total Interviews"
          value={summaryMetrics.totalInterviews.current.toLocaleString()}
          trendValue={formatTrend(summaryMetrics.totalInterviews.change)}
          trendDirection={
            summaryMetrics.totalInterviews.change >= 0 ? "up" : "down"
          }
          icon={LuUsers}
        />
        <StatCard
          title="Positive Sentiment"
          value={`${summaryMetrics.positiveSentiment.current}%`}
          trendValue={formatTrend(summaryMetrics.positiveSentiment.change)}
          trendDirection={
            summaryMetrics.positiveSentiment.change >= 0 ? "up" : "down"
          }
          icon={LuSmile}
        />
        <StatCard
          title="Avg. Duration"
          value={`${summaryMetrics.avgDuration.current} min`}
          trendValue={formatTrend(summaryMetrics.avgDuration.change)}
          trendDirection={
            summaryMetrics.avgDuration.change >= 0 ? "up" : "down"
          }
          icon={LuClock}
        />
        <StatCard
          title="Top Product"
          value={summaryMetrics.topProduct.name}
          trendValue={formatTrend(summaryMetrics.topProduct.change) + " usage"}
          trendDirection={
            summaryMetrics.topProduct.change >= 0 ? "up" : "down"
          }
          icon={LuTrendingUp}
        />

        <div className="grid-col-span-3">
          <SpiderChart />
        </div>
        <div className="grid-col-span-2">
          <SentimentChart />
        </div>
        <div className="grid-col-span-4">
          <ProductChart />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
