import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Automatically attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('veriscope_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses (expired token)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('veriscope_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  signup: (email, username, password) =>
    api.post('/auth/signup', { email, username, password }),
  login: (email, password) =>
    api.post('/auth/login', { email, password }),
  me: () => api.get('/auth/me'),
};

export const researchAPI = {
  query: (prompt, mode = 'linear', sessionId = null) =>
    api.post('/research', { prompt, mode, session_id: sessionId }),
  stream: (prompt, mode = 'linear', sessionId = null, signal = null) => {
    const token = localStorage.getItem('veriscope_token');
    return fetch(`${API_BASE}/research/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ prompt, mode, session_id: sessionId }),
      signal,
    });
  },
};

export const sessionAPI = {
  list: () => api.get('/sessions'),
  get: (id) => api.get(`/sessions/${id}`),
  create: (title) => api.post('/sessions', { title }),
  delete: (id) => api.delete(`/sessions/${id}`),
};

export default api;
