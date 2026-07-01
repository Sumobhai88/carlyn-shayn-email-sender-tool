/**
 * Central API utility - automatically adds auth token to every request
 * On 401, clears token and redirects to login
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';

const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
};

/** Called when any request returns 401 - clears session and reloads */
const handleUnauthorized = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  // Force full page reload so App.jsx re-checks auth → shows login page
  window.location.reload();
};

/** Wrap fetch response - auto-handle 401 */
const handleResponse = (res) => {
  if (res.status === 401) {
    handleUnauthorized();
  }
  return res;
};

export const api = {
  get: (path) =>
    fetch(`${API_URL}${path}`, {
      headers: getAuthHeaders()
    }).then(handleResponse),

  post: (path, body) =>
    fetch(`${API_URL}${path}`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: body ? JSON.stringify(body) : undefined
    }).then(handleResponse),

  put: (path, body) =>
    fetch(`${API_URL}${path}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: body ? JSON.stringify(body) : undefined
    }).then(handleResponse),

  delete: (path) =>
    fetch(`${API_URL}${path}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    }).then(handleResponse),

  postForm: (path, formData) =>
    fetch(`${API_URL}${path}`, {
      method: 'POST',
      headers: {
        ...(localStorage.getItem('access_token')
          ? { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
          : {})
      },
      body: formData
    }).then(handleResponse)
};

export default API_URL;
