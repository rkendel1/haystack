import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { Document } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileText, Trash2, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

export default function DocumentList() {
  const { data: documents, isLoading, refetch } = useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      const { data } = await api.get<Document[]>('/documents');
      return data;
    },
  });

  const handleDelete = async (documentId: string) => {
    try {
      await api.delete(`/documents/${documentId}`);
      toast.success('Document deleted successfully');
      refetch();
    } catch (error: any) {
      toast.error(`Failed to delete document: ${error.message}`);
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6 flex items-center justify-center">
          <Loader2 className="h-6 w-6 animate-spin text-primary" />
        </CardContent>
      </Card>
    );
  }

  if (!documents || documents.length === 0) {
    return (
      <Card>
        <CardContent className="p-6 text-center text-muted-foreground">
          No documents uploaded yet
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Indexed Documents</CardTitle>
      </CardHeader>
      <CardContent className="p-6 pt-0">
        <div className="space-y-2">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="flex items-center justify-between p-3 rounded-md border bg-card hover:bg-accent/50 transition-colors"
            >
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <FileText className="h-5 w-5 text-primary flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">
                    {doc.meta?.name || doc.meta?.file_path || doc.id}
                  </p>
                  {doc.meta?.size && (
                    <p className="text-xs text-muted-foreground">
                      {(doc.meta.size / 1024).toFixed(2)} KB
                    </p>
                  )}
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleDelete(doc.id)}
                className="flex-shrink-0"
              >
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
