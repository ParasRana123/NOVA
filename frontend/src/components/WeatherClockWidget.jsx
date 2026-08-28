import React, { useState, useEffect } from 'react';

export default function WeatherClockWidget({ weatherData, onRefreshWeather }) {
  const [currentTime, setCurrentTime] = useState('');
  const [currentDate, setCurrentDate] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const timeStr = now.toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
      const dateStr = now.toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric'
      });
      setCurrentTime(timeStr);
      setCurrentDate(dateStr);
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="weather-clock-widget">
      {/* Digital LED Clock */}
      <div className="digital-clock-card">
        <div className="digital-date">{currentDate}</div>
        <div className="digital-clock-display" title="System Local Time">
          {currentTime || '--:--:--'}
        </div>
      </div>

      {/* Live Weather Telemetry */}
      <div className="weather-card" onClick={onRefreshWeather} title="Click to refresh weather">
        <div className="weather-header">
          <div className="weather-icon-wrapper">
            <img
              src="/weather.jpg"
              alt="Weather"
              className="weather-badge-icon"
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
            <span className="weather-title">LOCAL WEATHER</span>
          </div>
          <span className="refresh-hint">↻</span>
        </div>

        <div className="weather-body">
          <div className="weather-temp-desc">
            {weatherData?.weather || 'Loading Weather...'}
          </div>
          {weatherData?.location && (
            <div className="weather-location">
              📍 {weatherData.location}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
