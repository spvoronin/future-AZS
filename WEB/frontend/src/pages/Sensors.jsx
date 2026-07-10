import { useEffect, useState } from 'react';
import { Api } from '../api/api';

export default function Sensors() {
  const [sensorData, setSensorData] = useState(null);
  const [error, setError] = useState('');

  const fetchSensors = async () => {
    try {
      const data = await Api.getSensors();
      if (data.status === 'error') {
        setError(data.message);
      } else {
        setSensorData(data);
        setError('');
      }
    } catch (err) {
      setError('Не удалось загрузить данные с датчиков');
    }
  };

  useEffect(() => {
    fetchSensors();
    // Обновляем данные каждые 5 секунд
    const interval = setInterval(fetchSensors, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="card">
      <h3 style={{ textAlign: 'left' }}>Мониторинг резервуаров (IoT)</h3>
      {error && <div className="error-text">{error}</div>}

      {!sensorData && !error ? (
        <div className="empty-note">Ожидание данных...</div>
      ) : sensorData && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
          <div className="info-row">
            <span className="label">Уровень топлива</span>
            <span className="value"><b>{sensorData.water_level} %</b></span>
          </div>
          <div className="info-row">
            <span className="label">Температура внутри</span>
            <span className="value">{sensorData.tank_temperature} °C</span>
          </div>
          <div className="info-row">
            <span className="label">Температура среды</span>
            <span className="value">{sensorData.ambient_temperature} °C</span>
          </div>
          <div className="info-row">
            <span className="label">Влажность среды</span>
            <span className="value">{sensorData.ambient_humidity} %</span>
          </div>
          <div className="info-row">
            <span className="label">Газ (MQ-2)</span>
            <span className="value">{sensorData.gas} ppm</span>
          </div>
          <div className="info-row">
            <span className="label">Датчик пламени</span>
            <span className="value" style={{ color: sensorData.flame ? 'red' : 'green' }}>
              {sensorData.flame ? 'ОБНАРУЖЕНО' : 'Норма'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}