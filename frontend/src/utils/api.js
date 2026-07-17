import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (data) => api.post('/api/auth/login', data),
  register: (data) => api.post('/api/auth/register', data),
  me: () => api.get('/api/auth/me'),
  toggleDarkMode: (dark_mode) => api.patch('/api/auth/dark-mode', null, { params: { dark_mode } }),
};

export const scanAPI = {
  upload: (formData) => api.post('/api/scans/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000,
  }),
  list: () => api.get('/api/scans/'),
  get: (id) => api.get(`/api/scans/${id}`),
  delete: (id) => api.delete(`/api/scans/${id}`),
  downloadPDF: (id) => `${API_BASE}/api/scans/${id}/pdf?token=${localStorage.getItem('token')}`,
  addComment: (id, data) => api.post(`/api/scans/${id}/comments`, data),
  listComments: (id) => api.get(`/api/scans/${id}/comments`),
};

export const teamAPI = {
  create: (data) => api.post('/api/teams/', data),
  join: (data) => api.post('/api/teams/join', data),
  getMine: () => api.get('/api/teams/me'),
  members: () => api.get('/api/teams/members'),
  leave: () => api.delete('/api/teams/leave'),
};

export const dashboardAPI = {
  get: () => api.get('/api/dashboard/'),
};

export default api;
