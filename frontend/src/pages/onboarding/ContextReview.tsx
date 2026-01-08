import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listContexts, confirmContext, rejectContext, updateContext } from '@/lib/contextApi';
import { ContextObject, ContextObjectUpdate } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Check, X, Edit2, Building2, Scale, Users, TrendingUp, Shield, Lightbulb, ExternalLink } from 'lucide-react';
import { toast } from 'sonner';

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  company: Building2,
  regulation: Scale,
  persona: Users,
  competitor: TrendingUp,
  industry: Shield,
  assumption: Lightbulb,
};

const CATEGORY_LABELS: Record<string, string> = {
  company: 'Company Profile',
  regulation: 'Applicable Regulations',
  persona: 'Customer Personas',
  competitor: 'Competitive Landscape',
  industry: 'Industry Classification',
  assumption: 'Baseline Assumptions',
};

interface ContextReviewProps {
  onComplete: () => void;
  sessionId: string;
}

export default function ContextReview({ onComplete }: ContextReviewProps) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState<Record<string, any>>({});
  const [editError, setEditError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: contexts, isLoading } = useQuery({
    queryKey: ['contexts', 'pending'],
    queryFn: () => listContexts({ status: 'pending' }),
  });

  const confirmMutation = useMutation({
    mutationFn: confirmContext,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contexts'] });
      toast.success('Context confirmed');
    },
  });

  const rejectMutation = useMutation({
    mutationFn: rejectContext,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contexts'] });
      toast.success('Context rejected');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, update }: { id: string; update: ContextObjectUpdate }) =>
      updateContext(id, update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contexts'] });
      setEditingId(null);
      toast.success('Context updated');
    },
  });

  const handleEdit = (context: ContextObject) => {
    setEditingId(context.id);
    setEditContent(context.content);
    setEditError(null);
  };

  const handleSaveEdit = (id: string) => {
    if (editError) {
      toast.error('Please fix JSON errors before saving');
      return;
    }
    updateMutation.mutate({ id, update: { content: editContent } });
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditContent({});
    setEditError(null);
  };

  const handleComplete = () => {
    const pendingCount = contexts?.filter((c) => c.status === 'pending').length || 0;
    if (pendingCount > 0) {
      const confirmed = window.confirm(
        `You have ${pendingCount} pending items. Are you sure you want to continue?`
      );
      if (!confirmed) return;
    }
    onComplete();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div>Loading contexts...</div>
      </div>
    );
  }

  // Group contexts by type
  const groupedContexts: Record<string, ContextObject[]> = {};
  contexts?.forEach((context) => {
    if (!groupedContexts[context.type]) {
      groupedContexts[context.type] = [];
    }
    groupedContexts[context.type].push(context);
  });

  const confirmedCount = contexts?.filter((c) => c.status === 'confirmed').length || 0;
  const totalCount = contexts?.length || 0;

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-4xl mx-auto space-y-6 py-8">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold">Review Your Business Context</h1>
          <p className="text-muted-foreground">
            We've discovered the following context about your business. Please review, edit, or approve each item.
          </p>
          <div className="text-sm text-muted-foreground">
            {confirmedCount} of {totalCount} confirmed
          </div>
        </div>

        {/* Context Categories */}
        {Object.entries(groupedContexts).map(([type, items]) => {
          const Icon = CATEGORY_ICONS[type] || Shield;
          const label = CATEGORY_LABELS[type] || type;

          return (
            <Card key={type}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Icon className="h-5 w-5" />
                  {label}
                  <span className="text-sm font-normal text-muted-foreground ml-2">
                    ({items.length} {items.length === 1 ? 'item' : 'items'})
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {items.map((context) => (
                  <div
                    key={context.id}
                    className={`p-4 rounded-lg border ${
                      context.status === 'confirmed'
                        ? 'bg-green-50 border-green-200'
                        : context.status === 'rejected'
                        ? 'bg-red-50 border-red-200'
                        : 'bg-secondary/50 border-border'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        {editingId === context.id ? (
                          <div className="space-y-2">
                            <textarea
                              value={JSON.stringify(editContent, null, 2)}
                              onChange={(e) => {
                                try {
                                  const parsed = JSON.parse(e.target.value);
                                  setEditContent(parsed);
                                  setEditError(null);
                                } catch (err) {
                                  setEditError((err as Error).message);
                                }
                              }}
                              className={`w-full p-2 border rounded font-mono text-sm ${
                                editError ? 'border-red-500' : ''
                              }`}
                              rows={8}
                            />
                            {editError && (
                              <div className="text-sm text-red-600">
                                Invalid JSON: {editError}
                              </div>
                            )}
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                onClick={() => handleSaveEdit(context.id)}
                                disabled={updateMutation.isPending || !!editError}
                              >
                                Save
                              </Button>
                              <Button size="sm" variant="outline" onClick={handleCancelEdit}>
                                Cancel
                              </Button>
                            </div>
                          </div>
                        ) : (
                          <>
                            <pre className="text-sm whitespace-pre-wrap font-sans">
                              {JSON.stringify(context.content, null, 2)}
                            </pre>
                            <div className="mt-2 flex items-center gap-4 text-xs text-muted-foreground">
                              <span>Source: {context.source}</span>
                              <span>Confidence: {(context.confidence * 100).toFixed(0)}%</span>
                              {context.evidence_refs.length > 0 && (
                                <a
                                  href={context.evidence_refs[0]}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="flex items-center gap-1 text-primary hover:underline"
                                >
                                  Evidence <ExternalLink className="h-3 w-3" />
                                </a>
                              )}
                            </div>
                          </>
                        )}
                      </div>
                      {context.status === 'pending' && editingId !== context.id && (
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleEdit(context)}
                            title="Edit"
                          >
                            <Edit2 className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => confirmMutation.mutate(context.id)}
                            disabled={confirmMutation.isPending}
                            className="text-green-600 hover:text-green-700"
                            title="Approve"
                          >
                            <Check className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => rejectMutation.mutate(context.id)}
                            disabled={rejectMutation.isPending}
                            className="text-red-600 hover:text-red-700"
                            title="Reject"
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          );
        })}

        {/* Footer Actions */}
        <div className="flex justify-center gap-4">
          <Button variant="outline" onClick={() => window.location.reload()}>
            Review Later
          </Button>
          <Button onClick={handleComplete} size="lg">
            Complete Onboarding
          </Button>
        </div>
      </div>
    </div>
  );
}
