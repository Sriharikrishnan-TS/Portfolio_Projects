import React from "react";
import { FaArrowUp, FaArrowDown } from "react-icons/fa";

const StatCard = ({
  title,
  value,
  trendValue,
  trendDirection,
  icon: IconComponent,
}) => {
  const isPositive = trendDirection === "up";
  const trendColorClass = isPositive ? "trend-positive" : "trend-negative";
  const TrendIcon = isPositive ? FaArrowUp : FaArrowDown;

  return (
    <div className="stat-card">
      <div className="stat-card-info">
        <p className="stat-card-title">{title}</p>
        <p className="stat-card-value">{value}</p>
        <div className="stat-card-trend">
          <span className={trendColorClass}>
            <TrendIcon /> {trendValue}
          </span>
          <span className="trend-text">from last week</span>
        </div>
      </div>
      <div className="stat-card-icon">
        <IconComponent size={28} />
      </div>
    </div>
  );
};

export default StatCard;
