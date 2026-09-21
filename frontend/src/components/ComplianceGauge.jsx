import React from 'react';

export const ComplianceGauge = ({ score, size = 120, label = "Fleet Posture" }) => {
  const normalizedScore = Math.min(100, Math.max(0, score || 0));
  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (normalizedScore / 100) * circumference;

  let strokeColor = "#30ba78"; // SUSE Green
  if (normalizedScore < 70) {
    strokeColor = "#f43f5e"; // Rose
  } else if (normalizedScore < 85) {
    strokeColor = "#fbbf24"; // Amber
  }

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#1e293b"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-black text-slate-100">{normalizedScore}%</span>
          <span className="text-[10px] uppercase font-bold text-slate-400">Score</span>
        </div>
      </div>
      {label && <span className="mt-2 text-xs font-medium text-slate-300">{label}</span>}
    </div>
  );
};
