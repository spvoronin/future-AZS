import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Api } from './api/api';
import GasStation from './pages/GasStation';
import Profile from './pages/Profile';
import Sensors from './pages/Sensors';
import Register from './pages/Register';

function Sidebar() {
  const location = useLocation();
  const isActive = (path) => location.pathname === path ? 'active' : '';

  return (
    <div className="sidebar">
      <Link to="/profile" className={isActive('/profile')} title="Профиль">&#128100;</Link>
      <Link to="/" className={isActive('/')} title="Заправка">&#9981;</Link>
      <Link to="/sensors" className={isActive('/sensors')} title="Датчики">&#128246;</Link>
    </div>
  );
}

function Topbar({ onOpenLogin, stationLabel }) {
  const { user } = useAuth();
  return (
    <div className="topbar">
      <div className="logo">АЗС СИСТЕМА</div>
      <div className="station-badge">{stationLabel}</div>
      <button className="btn btn-outline" onClick={onOpenLogin}>
        {user ? user.first_name : 'Вход'}
      </button>
    </div>
  );
}

function LoginModal({ isOpen, onClose }) {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  if (!isOpen) return null;

  const handleSubmit = async () => {
    setError('');
    if (!email || !password) {
      setError('Заполните оба поля');
      return;
    }

    try {
      const res = await Api.login(email, password);
      if (res.code === 401 || res.message === "Unauthorized") {
        setError("Неверный email или пароль");
        return;
      }

      let userId = null;
      try {
        const allUsers = await Api.getAllUsers();
        const match = Array.isArray(allUsers) ? allUsers.find((u) => u.email === email) : null;
        if (match) userId = match.id;
      } catch (e) {
        console.warn("Не удалось получить id пользователя", e);
      }
      const userData = { ...res, id: userId, email };
      localStorage.setItem("azs_user", JSON.stringify(userData));
      login(userData);
      onClose();
    } catch (err) {
      setError(err.message || 'Ошибка сети');
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>Вход</h2>
        <div className="field">
          <label>Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="ivanov@mail.com" />
        </div>
        <div className="field">
          <label>Пароль</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" />
        </div>
        {error && <div className="error-text">{error}</div>}
        <div className="modal-actions">
          <button className="btn" style={{ background: '#eee', color: '#000' }} onClick={onClose}>Отмена</button>
          <button className="btn btn-red" onClick={handleSubmit}>Войти</button>
        </div>
        <div className="register-prompt">
            Нет аккаунта?
             <Link
                to="/register"
                onClick={onClose}
                style={{ color: 'blue' }}
             >
             Зарегистрироваться
             </Link>
        </div>
      </div>
    </div>
  );
}

function MainLayout() {
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [stationLabel, setStationLabel] = useState('Загрузка станции...');
  useEffect(() => {
    const handleOpen = () => setIsLoginOpen(true);
    window.addEventListener('open-login-modal', handleOpen);
    return () => window.removeEventListener('open-login-modal', handleOpen);
  }, []);
  return (
    <div className="app">
      <Sidebar />
      <div className="main">
        <Topbar onOpenLogin={() => setIsLoginOpen(true)} stationLabel={stationLabel} />
        <div className="content">
          <Routes>
            <Route path="/" element={<GasStation setStationLabel={setStationLabel} />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/sensors" element={<Sensors />} />
            <Route path="/register" element={<Register />} />
          </Routes>
        </div>
      </div>
      <LoginModal isOpen={isLoginOpen} onClose={() => setIsLoginOpen(false)} />
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <MainLayout />
      </BrowserRouter>
    </AuthProvider>
  );
}