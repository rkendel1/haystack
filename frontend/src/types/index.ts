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
