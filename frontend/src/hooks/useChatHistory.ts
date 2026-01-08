import { useState, useEffect } from 'react';
import { ChatHistory, ChatMessage } from '@/types';

const STORAGE_KEY = 'haystack-chat-history';

export const useChatHistory = () => {
  const [histories, setHistories] = useState<ChatHistory[]>([]);
  const [currentHistoryId, setCurrentHistoryId] = useState<string | null>(null);

  // Load from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        setHistories(JSON.parse(stored));
      } catch (e) {
        console.error('Failed to parse chat history:', e);
      }
    }
  }, []);

  // Save to localStorage whenever histories change
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(histories));
  }, [histories]);

  const createHistory = (title: string): string => {
    const newHistory: ChatHistory = {
      id: Date.now().toString(),
      title,
      messages: [],
      created_at: Date.now(),
      updated_at: Date.now(),
    };
    setHistories([newHistory, ...histories]);
    setCurrentHistoryId(newHistory.id);
    return newHistory.id;
  };

  const addMessage = (historyId: string, message: ChatMessage) => {
    setHistories((prev) =>
      prev.map((h) =>
        h.id === historyId
          ? {
              ...h,
              messages: [...h.messages, message],
              updated_at: Date.now(),
            }
          : h
      )
    );
  };

  const deleteHistory = (historyId: string) => {
    setHistories((prev) => prev.filter((h) => h.id !== historyId));
    if (currentHistoryId === historyId) {
      setCurrentHistoryId(null);
    }
  };

  const getCurrentHistory = (): ChatHistory | null => {
    if (!currentHistoryId) return null;
    return histories.find((h) => h.id === currentHistoryId) || null;
  };

  return {
    histories,
    currentHistoryId,
    setCurrentHistoryId,
    createHistory,
    addMessage,
    deleteHistory,
    getCurrentHistory,
  };
};
