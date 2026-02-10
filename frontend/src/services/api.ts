import axios from 'axios';
import { ClassifiedInsight, DashboardStats, DashboardCharts } from '../types/feedback';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const submitSingleFeedback = async (data: { text: string; source: string }) => {
  const response = await api.post('/classify', data);
  return response.data;
};

export const uploadCSV = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/upload-csv', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const getClassifiedFeedback = async (limit: number = 50): Promise<ClassifiedInsight[]> => {
  const response = await api.get('/classified-feedback', { params: { limit } });
  return response.data;
};

export const getStats = async (): Promise<DashboardStats> => {
  const response = await api.get('/analytics/summary');
  return response.data;
};

export const getCharts = async (): Promise<DashboardCharts> => {
  const response = await api.get('/analytics/charts');
  return response.data;
};
export const getFeedbackById = async (id: string): Promise<ClassifiedInsight> => {
  const all = await getClassifiedFeedback();
  const match = all.find(item => item.id === id);
  if (!match) throw new Error('Not found');
  return match;
};

export default api;