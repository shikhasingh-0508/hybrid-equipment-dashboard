import React, { useState } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import 'chart.js/auto';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const uploadFile = async (e) => {
    if (!e.target.files[0]) return;
    const formData = new FormData();
    formData.append('file', e.target.files[0]);
    setLoading(true);

    try {
      const res = await axios.post('http://127.0.0.1:8000/api/upload/', formData);
      setData(res.data.summary);
    } catch (err) {
      alert("Upload failed. Ensure Django is running.");
    } finally {
      setLoading(false);
    }
  };

  const chartOptions = {
    animation: { duration: 2000, easing: 'easeOutBounce' },
    responsive: true,
    plugins: { legend: { display: true } }
  };

  return (
    <div style={{ padding: '40px', fontFamily: 'sans-serif', backgroundColor: '#f9f9f9' }}>
      <h1 style={{ textAlign: 'center' }}>Chemical Plant Safety Web Portal</h1>
      <div style={{ background: '#white', padding: '20px', borderRadius: '10px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
        <input type="file" onChange={uploadFile} accept=".csv" />
        {loading && <p>Analyzing Safety Data...</p>}
        
        {data && (
          <div style={{ marginTop: '20px' }}>
            <h2 style={{ color: data.max_pressure > 7.0 ? '#e74c3c' : '#2c3e50' }}>
              Safety Status: {data.max_pressure > 7.0 ? "CRITICAL ALERT" : "OPERATIONAL"}
            </h2>
            <div style={{ height: '400px' }}>
              <Bar 
                options={chartOptions}
                data={{
                  labels: Object.keys(data.type_dist),
                  datasets: [{
                    label: 'Equipment Units',
                    data: Object.values(data.type_dist),
                    backgroundColor: data.max_pressure > 7.0 ? 'rgba(231, 76, 60, 0.6)' : 'rgba(52, 152, 219, 0.6)',
                  }]
                }} 
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
export default App;