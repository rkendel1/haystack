import api from './api';
import {
  CompanyInfo,
  ContextObject,
  ContextObjectUpdate,
  OnboardingContextResponse,
  OnboardingSession,
} from '@/types';

// ============================================================================
// ONBOARDING API
// ============================================================================

export const startOnboarding = async (companyInfo: CompanyInfo): Promise<OnboardingSession> => {
  const response = await api.post<OnboardingSession>('/onboarding/start', companyInfo);
  return response.data;
};

export const getOnboardingContext = async (sessionId: string): Promise<OnboardingContextResponse> => {
  const response = await api.get<OnboardingContextResponse>(`/onboarding/${sessionId}/context`);
  return response.data;
};

// ============================================================================
// CONTEXT MANAGEMENT API
// ============================================================================

export const listContexts = async (params?: {
  type?: string;
  status?: string;
  source?: string;
  limit?: number;
  offset?: number;
}): Promise<ContextObject[]> => {
  const response = await api.get<ContextObject[]>('/context', { params });
  return response.data;
};

export const getContext = async (id: string): Promise<ContextObject> => {
  const response = await api.get<ContextObject>(`/context/${id}`);
  return response.data;
};

export const updateContext = async (id: string, update: ContextObjectUpdate): Promise<ContextObject> => {
  const response = await api.patch<ContextObject>(`/context/${id}`, update);
  return response.data;
};

export const deleteContext = async (id: string): Promise<void> => {
  await api.delete(`/context/${id}`);
};

export const confirmContext = async (id: string): Promise<ContextObject> => {
  const response = await api.post<ContextObject>(`/context/${id}/confirm`);
  return response.data;
};

export const rejectContext = async (id: string): Promise<ContextObject> => {
  const response = await api.post<ContextObject>(`/context/${id}/reject`);
  return response.data;
};
