import { useState } from 'react';
import { useHaystackQuery } from '@/hooks/useHaystackQuery';
import { PipelineMode, ChatMessage } from '@/types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import CitationCard from './CitationCard';
import { Send, Loader2, User, Bot } from 'lucide-react';

interface ChatProps {
  pipelineMode: PipelineMode;
  onMessageSent?: (message: ChatMessage) => void;
}

export default function Chat({ pipelineMode, onMessageSent }: ChatProps) {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  
  const { isLoading, error, refetch } = useHaystackQuery(
    { query, pipeline: pipelineMode, top_k: 5 },
    false
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      role: 'user',
      content: query,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    onMessageSent?.(userMessage);
    setQuery('');

    try {
      const result = await refetch();
      if (result.data) {
        const assistantMessage: ChatMessage = {
          id: `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
          role: 'assistant',
          content: result.data.answer,
          documents: result.data.documents,
          steps: result.data.steps,
          timestamp: Date.now(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
        onMessageSent?.(assistantMessage);
      }
    } catch (err) {
      console.error('Query failed:', err);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-muted-foreground py-12">
            <Bot className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p>Start a conversation by asking a question</p>
          </div>
        )}
        
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.role === 'assistant' && (
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                  <Bot className="h-5 w-5 text-primary-foreground" />
                </div>
              </div>
            )}
            
            <div
              className={`max-w-[80%] ${
                message.role === 'user' ? 'order-1' : 'order-2'
              }`}
            >
              <Card
                className={`${
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                }`}
              >
                <div className="p-4">
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>
              </Card>
              
              {message.role === 'assistant' && message.documents && (
                <div className="mt-2">
                  <CitationCard documents={message.documents} />
                </div>
              )}
              
              {message.role === 'assistant' && message.steps && (
                <div className="mt-2 space-y-1">
                  <p className="text-xs text-muted-foreground font-semibold">
                    Agent Steps:
                  </p>
                  {message.steps.map((step, i) => (
                    <Card key={i} className="bg-muted/50">
                      <div className="p-2 text-xs">
                        <p className="font-medium">Step {step.step}: {step.action}</p>
                        <p className="text-muted-foreground">{step.observation}</p>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>

            {message.role === 'user' && (
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center">
                  <User className="h-5 w-5 text-secondary-foreground" />
                </div>
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                <Bot className="h-5 w-5 text-primary-foreground" />
              </div>
            </div>
            <Card className="bg-muted">
              <div className="p-4 flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm">Thinking...</span>
              </div>
            </Card>
          </div>
        )}

        {error && (
          <Card className="bg-destructive/10 border-destructive">
            <div className="p-4">
              <p className="text-sm text-destructive">
                Error: {error.message}
              </p>
            </div>
          </Card>
        )}
      </div>

      {/* Input area */}
      <div className="border-t p-4 bg-background">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button type="submit" disabled={isLoading || !query.trim()}>
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </form>
      </div>
    </div>
  );
}
