import axios from 'axios';
import { GenerationRequest, GenerationResponse } from '../types';

const api = axios.create({
  baseURL: '/api',
});

export async function generateIdeas(request: GenerationRequest): Promise<GenerationResponse> {
  const response = await api.post<GenerationResponse>('/generate', request);
  return response.data;
}
