import React, { useState } from 'react';
import { Api } from '../api/api';
import { Link } from 'react-router-dom';

export default function Register() {
  const [formData, setFormData] = useState({
    phone: '',
    email: '',
    password_hash: '',
    first_name: '',
    number_of_car: ''
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await Api.register(formData);
      alert('Успешная регистрация! Теперь вы можете войти.');
    } catch (err) {
      alert('Ошибка при регистрации: ' + err.message);
    }
  };

  return (
    <div className="card register-card">
      <h2 style={{ textAlign: 'center', color: 'var(--red)', marginBottom: '20px' }}>Регистрация</h2>

      <form onSubmit={handleSubmit}>
        <div className="field">
          <label>Имя</label>
          <input name="first_name" onChange={handleChange} required />
        </div>

        <div className="field">
          <label>Телефон</label>
          <input name="phone" onChange={handleChange} required />
        </div>

        <div className="field">
          <label>Email</label>
          <input name="email" type="email" onChange={handleChange} required />
        </div>

        <div className="field">
          <label>Пароль</label>
          <input name="password_hash" type="password" onChange={handleChange} required />
        </div>

        <div className="field">
          <label>Номер автомобиля</label>
          <input name="number_of_car" onChange={handleChange} />
        </div>

        <button type="submit" className="btn btn-red" style={{ width: '100%', marginTop: '10px' }}>
          Создать аккаунт
        </button>
      </form>

      <div className="register-prompt">
        Уже есть аккаунт? <Link to="/" className="register-link">Войти</Link>
      </div>
    </div>
  );
}