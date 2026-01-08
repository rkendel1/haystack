import { Document } from '@/types';
import { Card, CardContent } from '@/components/ui/card';
import { FileText } from 'lucide-react';

interface CitationCardProps {
  documents: Document[];
}

export default function CitationCard({ documents }: CitationCardProps) {
  if (!documents || documents.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 space-y-2">
      <h3 className="text-sm font-semibold text-muted-foreground">Sources</h3>
      {documents.map((doc, index) => (
        <Card key={index} className="bg-muted/50">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <FileText className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <p className="text-sm font-medium truncate">
                    {doc.meta?.name || doc.meta?.file_path || `Document ${index + 1}`}
                  </p>
                  {doc.score && (
                    <span className="text-xs text-muted-foreground whitespace-nowrap">
                      Score: {doc.score.toFixed(3)}
                    </span>
                  )}
                </div>
                <p className="text-sm text-muted-foreground line-clamp-3">
                  {doc.content}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
