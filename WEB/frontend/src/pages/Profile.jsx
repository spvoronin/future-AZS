import React from 'react';
import { useAuth } from '../context/AuthContext'; // Используем наш контекст авторизации

export default function Profile() {
  const { user, logout } = useAuth(); // Достаем данные юзера и функцию выхода

  return (
    <div className="profile-content">
      <div className="card">
        <div className="profile-header">
          <div className="avatar-circle" id="avatarLetter">
            {user ? user.first_name[0].toUpperCase() : '?'}
          </div>
          <div>
            <div className="profile-name" id="profileName">
              {user ? user.first_name : 'Вы не вошли в аккаунт'}
            </div>
          </div>
        </div>

        <div className="info-row"><span className="label">E-mail</span><span className="value" id="infoEmail">{user ? user.email : '—'}</span></div>
        <div className="info-row"><span className="label">номер телефона</span><span className="value" id="infoPhone">{user ? user.phone : '—'}</span></div>
        <div className="info-row"><span className="label">номер машины</span><span className="value" id="infoCar">{user ? user.number_of_car : '—'}</span></div>
        <div className="info-row">
          <span className="label">баланс</span>
          <span className="value" id="infoBalance">нет данных <span className="empty-note">(нет в API)</span></span>
        </div>
        <div className="info-row">
          <span className="label">водительские права</span>
          <span className="value"><a href="#">добавить</a></span>
        </div>

        <div className="card loyalty-card" style={{ boxShadow: 'none', borderStyle: 'dashed' }}>
          <h3 style={{ textAlign: 'left' }}>Карта лояльности</h3>
          <div className="empty-note">Бэкенд хранит карты лояльности в БД, но для них ещё нет API-роутов — здесь заглушка.</div>
          <div className="loyalty-numbers">
            <span>номер: **** **** **** ****</span>
          </div>
          <button className="btn btn-red qr-btn" disabled>показать QR-код</button>
        </div>
      </div>

      <div className="card">
        <h3 style={{ textAlign: 'left' }}>Настройки</h3>
        <div className="settings-title">Персональные настройки</div>
        <div className="settings-item">Способы оплаты</div>
        <div className="settings-item">Оформление</div>
        <div className="settings-item">Уведомления</div>
        <div className="settings-title">Безопасность</div>
        <div className="settings-item">Подключённые устройства</div>
        <div className="settings-item">Удалить учётную запись</div>
        <hr className="settings-divider" />
        {user && (
          <div className="settings-item" id="logoutItem" onClick={logout}>
            Выйти из аккаунта
          </div>
        )}
        <div className="settings-item">О приложении</div>
      </div>
    </div>
  );
}