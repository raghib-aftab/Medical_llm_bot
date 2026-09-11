import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';
const LOGIN_TIME_KEY = 'auth_login_time';
const TOKEN_EXPIRY_MS = 2 * 24 * 60 * 60 * 1000; // 2 days in milliseconds

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const getUser = () => {
  const user = localStorage.getItem(USER_KEY);
  return user ? JSON.parse(user) : null;
};

export const isTokenExpired = () => {
  const loginTime = localStorage.getItem(LOGIN_TIME_KEY);
  if (!loginTime) return true;
  const elapsed = Date.now() - parseInt(loginTime, 10);
  return elapsed >= TOKEN_EXPIRY_MS;
};

export const setAuthData = (token, user) => {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  localStorage.setItem(LOGIN_TIME_KEY, Date.now().toString());
};

export const clearAuthData = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(LOGIN_TIME_KEY);
};

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Skip redirect for auth endpoints (login/signup failures should show error, not reload)
    const isAuthEndpoint = error.config?.url?.startsWith('/api/auth/');
    if (error.response?.status === 401 && !isAuthEndpoint) {
      clearAuthData();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  // Signup
  signup: async (email, password, name, phone = null) => {
    const response = await api.post('/api/auth/signup', { email, password, name, phone });
    const { access_token, user } = response.data;
    setAuthData(access_token, user);
    return response.data;
  },

  login: async (email, password) => {
    const response = await api.post('/api/auth/login', { email, password });
    const { access_token, user } = response.data;
    setAuthData(access_token, user);
    return response.data;
  },

  // Forgot password
  forgotPassword: async (email) => {
    const response = await api.post('/api/auth/forgot-password', { email });
    return response.data;
  },

  logout: () => {
    clearAuthData();
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  isAuthenticated: () => {
    return !!getToken();
  },
};

export const chatAPI = {
  // Create a new chat
  createChat: async () => {
    const response = await api.post('/api/chats');
    return response.data;
  },

  // Get all chats
  getAllChats: async () => {
    const response = await api.get('/api/chats');
    return response.data;
  },

  // Get a specific chat
  getChat: async (chatId) => {
    const response = await api.get(`/api/chats/${chatId}`);
    return response.data;
  },

  // Delete a chat
  deleteChat: async (chatId) => {
    const response = await api.delete(`/api/chats/${chatId}`);
    return response.data;
  },

  // Send a message
  sendMessage: async (chatId, content) => {
    const response = await api.post(`/api/chats/${chatId}/messages`, {
      content,
    });
    return response.data;
  },
};

// Profile API
export const profileAPI = {
  // Get current user profile
  getProfile: async () => {
    const response = await api.get('/api/profile');
    return response.data;
  },

  // Update profile
  updateProfile: async (data) => {
    const response = await api.put('/api/profile', data);
    // Update local storage with new user data
    const currentUser = getUser();
    if (currentUser) {
      const updatedUser = { ...currentUser, ...data };
      localStorage.setItem(USER_KEY, JSON.stringify(updatedUser));
    }
    return response.data;
  },

  // Update password
  updatePassword: async (currentPassword, newPassword) => {
    const response = await api.put('/api/profile/password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  },
};

// Appointments API
export const appointmentsAPI = {
  // Get all doctors
  getDoctors: async (specialization = null) => {
    const params = specialization ? { specialization } : {};
    const response = await api.get('/api/appointments/doctors', { params });
    return response.data;
  },

  // Get single doctor
  getDoctor: async (doctorId) => {
    const response = await api.get(`/api/appointments/doctors/${doctorId}`);
    return response.data;
  },

  // Get all specializations
  getSpecializations: async () => {
    const response = await api.get('/api/appointments/specializations');
    return response.data;
  },

  // Create appointment
  createAppointment: async (appointmentData) => {
    const response = await api.post('/api/appointments', appointmentData);
    return response.data;
  },

  // Get user appointments
  getAppointments: async (statusFilter = null) => {
    const params = statusFilter ? { status_filter: statusFilter } : {};
    const response = await api.get('/api/appointments', { params });
    return response.data;
  },

  // Get single appointment
  getAppointment: async (appointmentId) => {
    const response = await api.get(`/api/appointments/${appointmentId}`);
    return response.data;
  },

  // Update appointment
  updateAppointment: async (appointmentId, updateData) => {
    const response = await api.put(`/api/appointments/${appointmentId}`, updateData);
    return response.data;
  },

  // Cancel appointment
  cancelAppointment: async (appointmentId) => {
    const response = await api.delete(`/api/appointments/${appointmentId}`);
    return response.data;
  },
};

// Hospitals API
export const hospitalsAPI = {
  // Get all hospitals
  getHospitals: async (filters = {}) => {
    const params = {};
    if (filters.city) params.city = filters.city;
    if (filters.specialization) params.specialization = filters.specialization;
    if (filters.emergencyOnly) params.emergency_only = true;
    
    const response = await api.get('/api/hospitals', { params });
    return response.data;
  },

  // Get single hospital
  getHospital: async (hospitalId) => {
    const response = await api.get(`/api/hospitals/${hospitalId}`);
    return response.data;
  },

  // Get all cities
  getCities: async () => {
    const response = await api.get('/api/hospitals/cities');
    return response.data;
  },

  // Get all specializations
  getSpecializations: async () => {
    const response = await api.get('/api/hospitals/specializations');
    return response.data;
  },
};

export default api;
