import axios from 'axios';

const API_BASE_URL = `${import.meta.env.VITE_API_URL}/api/v1`;

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors (logout)
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

// Auth API
export const authAPI = {
  login: (email, password) =>
    api.post('/auth/login', { email, password }),
  
  register: (email, password) =>
    api.post('/auth/register', { email, password }),
  
  getCurrentUser: () =>
    api.get('/auth/me'),
};

// Projects API
export const projectsAPI = {
  list: () =>
    api.get('/projects'),
  
  get: (id) =>
    api.get(`/projects/${id}`),
  
  create: (data) =>
    api.post('/projects', data),
  
  update: (id, data) =>
    api.put(`/projects/${id}`, data),
  
  delete: (id) =>
    api.delete(`/projects/${id}`),
  
  addMember: (projectId, userId) =>
    api.post(`/projects/${projectId}/members`, { user_id: userId }),
  
  removeMember: (projectId, userId) =>
    api.delete(`/projects/${projectId}/members/${userId}`),
};

// Issues API
export const issuesAPI = {
  list: (params) =>
    api.get('/issues', { params }),
  
  get: (id) =>
    api.get(`/issues/${id}`),
  
  create: (data) =>
    api.post('/issues', data),
  
  update: (id, data) =>
    api.put(`/issues/${id}`, data),
  
  delete: (id) =>
    api.delete(`/issues/${id}`),
  
  getAuditLog: (id) =>
    api.get(`/issues/${id}/audit`),
};

// Comments API
export const commentsAPI = {
  create: (data) =>
    api.post('/comments', data),
  
  update: (id, data) =>
    api.put(`/comments/${id}`, data),
  
  delete: (id) =>
    api.delete(`/comments/${id}`),
};

// Users API
export const usersAPI = {
  list: () =>
    api.get('/users'),
  
  get: (id) =>
    api.get(`/users/${id}`),
};

export default api;