import axios from 'axios'

axios.interceptors.response.use(response => {
  return response;
}, (error) => {
  return Promise.reject(error);
})

export const HTTP = axios.create({
  baseURL: '/api/',
  headers: {
    'client': 'vue2'
  }
})
