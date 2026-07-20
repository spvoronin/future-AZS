import React, { useState, useEffect } from 'react';
import { Api } from '../api/api';
import { useAuth } from '../context/AuthContext';

export default function GasStation({ setStationLabel }) {
  const { user } = useAuth();

  // Состояния (State) приложения вместо глобального объекта из main.js
  const [stationId, setStationId] = useState(null);
  const [prices, setPrices] = useState([]);
  const [pumps, setPumps] = useState([]);
  const [selectedFuel, setSelectedFuel] = useState(null);
  const [selectedPumpId, setSelectedPumpId] = useState(null);
  const [selectedVolume, setSelectedVolume] = useState(20);
  const [customVol, setCustomVol] = useState('');
  const [payError, setPayError] = useState('');

  // Загрузка данных при старте компонента
  useEffect(() => {
    async function loadStationAndData() {
      try {
        const stations = await Api.getStations();
        if (!Array.isArray(stations) || stations.length === 0) {
          if (setStationLabel) setStationLabel("Нет доступных АЗС");
          return;
        }

        const station = stations[0];
        setStationId(station.id);
        if (setStationLabel) setStationLabel(`АЗС №${station.id} — ${station.adress}`);

        // Загружаем цены
        const pricesData = await Api.getPrices(station.id);
        if (Array.isArray(pricesData)) {
          setPrices(pricesData);
          if (pricesData.length > 0) setSelectedFuel(pricesData[0].fuel_type);
        }

        // Загружаем колонки
        const pumpsData = await Api.getStationPumps(station.id);
        if (Array.isArray(pumpsData)) {
          setPumps(pumpsData);
        }
      } catch (err) {
        console.error(err);
        if (setStationLabel) setStationLabel("Ошибка соединения с сервером");
      }
    }
    loadStationAndData();
  }, [setStationLabel]);

  // Обработчики кликов
  const handleVolumeBtnClick = (vol) => {
    setCustomVol('');
    setSelectedVolume(vol);
  };

  const handleCustomVolChange = (e) => {
    const val = e.target.value;
    setCustomVol(val);
    const parsed = parseFloat(val);
    if (!isNaN(parsed) && parsed > 0) {
      setSelectedVolume(parsed);
    }
  };

  // Вычисления для панели "Итого" выполняются автоматически при изменении стейта
  const currentPriceEntry = prices.find((p) => p.fuel_type === selectedFuel);
  const pricePerLiter = currentPriceEntry ? currentPriceEntry.prices_per_liter : 0;
  const totalCost = (pricePerLiter * selectedVolume).toFixed(2);

  // Оформление заказа (Оплата)
  const handlePay = async () => {
    setPayError('');
    const currentPump = pumps.find(p => p.id === selectedPumpId);
    if (!user) {
      setPayError('Сначала войдите в аккаунт через верхнюю панель');
      return;
    }
    if (!currentPump) {
      setPayError('Выберите свободную колонку (зеленую)');
      return;
    }
    if (!selectedFuel) {
      setPayError('Выберите вид топлива');
      return;
    }

    try {
      const payload = {
        user_id: user.id,
        pump_id: currentPump.id,
        fuel_type: selectedFuel,
        requested_liters: selectedVolume
      };

      const res = await Api.createTransaction(payload);

      alert(`Заказ №${res.transaction_id} оформлен!\nК оплате: ${res.total_cost_rub} ₽\nНалив запущен.`);

      // Перезагружаем колонки, чтобы отобразить новый статус (например, dispensing)
      const updatedPumps = await Api.getStationPumps(stationId);
      if (Array.isArray(updatedPumps)) setPumps(updatedPumps);
      setSelectedPumpId(null); // сбрасываем текущий выбор
    } catch (err) {
      setPayError(err.message || 'Ошибка оформления заказа');
    }
  };

  const getStatusText = (p, isFree) => {
    if (!p.is_active) return "недоступна";
    if (p.status === "idle") return "свободна";
    if (p.status === "dispensing") return "идёт налив";
    return "сбой";
  };

  return (
    <>
      {/* Колонка 1: Цены и Колонки */}
      <div>
        <div className="card" style={{ marginBottom: '20px' }}>
          <h3>Цены на топливо</h3>
          <div className="prices-row">
            {prices.length === 0 ? (
              <div className="empty-note">Загрузка цен...</div>
            ) : (
              prices.map((p) => (
                <div
                  key={`price-${p.fuel_type}`}
                  className={`price-card ${selectedFuel === p.fuel_type ? 'selected' : ''}`}
                  onClick={() => setSelectedFuel(p.fuel_type)}
                >
                  <div className="fuel-name">{p.fuel_type}</div>
                  <div className="fuel-price">{p.prices_per_liter} ₽/л</div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="card">
          <h3>Колонки</h3>
          <div className="pumps-row">
            {pumps.length === 0 ? (
              <div className="empty-note">Загрузка колонок...</div>
            ) : (
              pumps.map((p) => {
                const isFree = p.is_active && p.status === "idle";
                const isSelected = p.id === selectedPumpId;

                // Рассчитываем класс стиля динамически
                let cardClass = "pump-card ";
                if (isSelected) cardClass += "selected";
                else if (!p.is_active) cardClass += "disabled";
                else if (p.status === "idle") cardClass += "free";
                else cardClass += "busy";

                return (
                  <div
                    key={`pump-${p.pump_number}-${p.id}`}
                    className={cardClass}
                    onClick={() => isFree && setSelectedPumpId(p.id)}
                    style={{ cursor: isFree ? 'pointer' : 'not-allowed' }}
                  >
                    <div className="pump-title">Колонка {p.pump_number}</div>
                    <div className="pump-status">{getStatusText(p, isFree)}</div>
                  </div>
                );
              })
            )}
          </div>
          <div className="your-station-box">
            <div className="row">&#8592; Ваша АЗС</div>
            <div className="row">
              {selectedPumpId
                ? `Колонка ${pumps.find(p => p.id === selectedPumpId)?.pump_number} выбрана` : 'Колонка не выбрана'}
            </div>
          </div>
        </div>
      </div>

      {/* Колонка 2: Услуги */}
      <div className="card">
        <h3>Услуги</h3>
        <label className="service-item"><input type="checkbox" /> Антифриз</label>
        <label className="service-item"><input type="checkbox" /> Банкомат</label>
        <label className="service-item"><input type="checkbox" /> Стеклоомывающая жидкость</label>
        <div className="service-note">
          оплата картой или QR-кодом<br />
          лимит 25 литров для физлиц<br />
          лимит 60 литров для юрлиц
        </div>
      </div>

      {/* Колонка 3: Покупка и калькулятор */}
      <div className="card">
        <h3>Покупка</h3>
        <div style={{ textAlign: 'center', fontSize: '13px', color: 'var(--text-muted)', marginBottom: '6px' }}>Объём</div>
        <div className="volume-row">
          {[10, 15, 20].map((vol) => (
            <button
              key={`vol-${vol}`}
              className={`volume-btn ${selectedVolume === vol && !customVol ? 'selected' : ''}`}
              onClick={() => handleVolumeBtnClick(vol)}
            >
              {vol}
            </button>
          ))}
          <input
            className="volume-custom"
            placeholder="…"
            type="number"
            min="1"
            value={customVol}
            onChange={handleCustomVolChange}
          />
        </div>

        <div className="summary-line">
          <span>общий объём:</span>
          <span>{selectedVolume} л</span>
        </div>
        <div className="summary-line">
          <span>цена за литр:</span>
          <span>{currentPriceEntry ? `${pricePerLiter} ₽/л` : '—'}</span>
        </div>
        <div className="summary-line total">
          <span>итого:</span>
          <span>{totalCost} ₽</span>
        </div>

        <button className="btn btn-red pay-btn" onClick={handlePay}>Оплатить</button>
        {payError && <div className="error-text">{payError}</div>}
      </div>
    </>
  );
}