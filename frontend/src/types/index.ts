export interface Document {
  id: string;
  content: string;
  meta: {
    name?: string;
    file_path?: string;
    file_type?: string;
    size?: number;
    [key: string]: any;
  };
  score?: number;
}

export interface QueryResponse {
  answer: string;
  documents: Document[];
  steps?: AgentStep[];
}

export interface AgentStep {
  step: number;
  action: string;
  observation: string;
}

export interface UploadResponse {
  message: string;
  document_id: string;
  file_name: string;
}

export type PipelineMode = 'rag' | 'agent' | 'search';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  documents?: Document[];
  steps?: AgentStep[];
  timestamp: number;
}

export interface ChatHistory {
  id: string;
  title: string;
  messages: ChatMessage[];
  created_at: number;
  updated_at: number;
}

// ============================================================================
// CONTEXT MANAGEMENT TYPES
// ============================================================================

export type ContextType = 'company' | 'industry' | 'regulation' | 'competitor' | 'persona' | 'assumption';
export type ContextSource = 'external' | 'inferred' | 'user';
export type ContextStatus = 'pending' | 'confirmed' | 'rejected';

export interface ContextObject {
  id: string;
  type: ContextType;
  content: Record<string, any>;
  source: ContextSource;
  confidence: number;
  status: ContextStatus;
  evidence_refs: string[];
  version: number;
  deleted_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ContextObjectUpdate {
  content?: Record<string, any>;
  status?: ContextStatus;
  confidence?: number;
  evidence_refs?: string[];
}

export interface OnboardingSession {
  id: string;
  user_id: string;
  company_name?: string;
  company_website?: string;
  industry?: string;
  current_step: string;
  status: 'in_progress' | 'completed' | 'abandoned';
  metadata: Record<string, any>;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface CompanyInfo {
  name: string;
  website: string;
  industry?: string;
}

export interface OnboardingContextResponse {
  session_id: string;
  contexts: ContextObject[];
  progress: {
    discovered: number;
    total_categories: number;
    categories: string[];
  };
}

