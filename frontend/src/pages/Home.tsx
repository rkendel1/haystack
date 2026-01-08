import { useState } from 'react';
import { PipelineMode, ChatMessage } from '@/types';
import Chat from '@/components/Chat';
import FileUploader from '@/components/FileUploader';
import DocumentList from '@/components/DocumentList';
import PipelineSwitcher from '@/components/PipelineSwitcher';
import { useChatHistory } from '@/hooks/useChatHistory';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { MessageSquare, FileText, Settings, Plus } from 'lucide-react';

export default function Home() {
  const [pipelineMode, setPipelineMode] = useState<PipelineMode>('rag');
  const [activeTab, setActiveTab] = useState<'chat' | 'documents'>('chat');
  const { createHistory, addMessage, currentHistoryId } = useChatHistory();

  const handleMessageSent = (message: ChatMessage) => {
    if (!currentHistoryId) {
      const newHistoryId = createHistory(message.content.slice(0, 50) + '...');
      addMessage(newHistoryId, message);
    } else {
      addMessage(currentHistoryId, message);
    }
  };

  const handleNewChat = () => {
    createHistory('New conversation');
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-primary flex items-center justify-center">
                <MessageSquare className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">Haystack RAG</h1>
                <p className="text-sm text-muted-foreground">
                  Powered by Retrieval-Augmented Generation
                </p>
              </div>
            </div>
            <Button onClick={handleNewChat} size="sm">
              <Plus className="h-4 w-4 mr-2" />
              New Chat
            </Button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 overflow-hidden">
        <div className="container mx-auto px-4 py-6 h-full">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
            {/* Left sidebar - Documents/Settings */}
            <div className="lg:col-span-1 space-y-6 overflow-y-auto">
              {/* Pipeline switcher */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Settings className="h-5 w-5" />
                    Pipeline Mode
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <PipelineSwitcher value={pipelineMode} onChange={setPipelineMode} />
                </CardContent>
              </Card>

              {/* Tabs for documents and file upload */}
              <div className="space-y-4">
                <div className="flex gap-2">
                  <Button
                    variant={activeTab === 'chat' ? 'default' : 'outline'}
                    onClick={() => setActiveTab('chat')}
                    size="sm"
                    className="flex-1"
                  >
                    <MessageSquare className="h-4 w-4 mr-2" />
                    Chat
                  </Button>
                  <Button
                    variant={activeTab === 'documents' ? 'default' : 'outline'}
                    onClick={() => setActiveTab('documents')}
                    size="sm"
                    className="flex-1"
                  >
                    <FileText className="h-4 w-4 mr-2" />
                    Documents
                  </Button>
                </div>

                {activeTab === 'documents' && (
                  <>
                    <FileUploader />
                    <DocumentList />
                  </>
                )}
              </div>
            </div>

            {/* Main chat area */}
            <div className="lg:col-span-2">
              <Card className="h-full flex flex-col">
                <Chat pipelineMode={pipelineMode} onMessageSent={handleMessageSent} />
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
