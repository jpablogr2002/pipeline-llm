import axios from 'axios';

// Creamos una instancia de Axios apuntando a tu backend local
const api = axios.create({
  baseURL: 'https://media-group-backend-183176360816.us-central1.run.app/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor: Antes de cada petición, si hay un token guardado, lo añade
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;