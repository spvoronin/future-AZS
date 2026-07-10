import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'; // ВОТ ЭТА СТРОЧКА СКОРЕЕ ВСЕГО СТЕРЛАСЬ

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
