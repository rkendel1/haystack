import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listContexts, confirmContext, rejectContext, deleteContext, updateContext } from '@/lib/contextApi';
import { ContextObject, ContextStatus, ContextSource, ContextType } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Building2, Scale, Users, TrendingUp, Shield, Lightbulb, Filter, Check, X, Trash2, Edit2, ExternalLink } from 'lucide-react';
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
  regulation: 'Regulations',
  persona: 'Customer Personas',
  competitor: 'Competitors',
  industry: 'Industry',
  assumption: 'Assumptions',
};

export default function ContextManagement() {
  const [filterStatus, setFilterStatus] = useState<ContextStatus | 'all'>('all');
  const [filterType, setFilterType] = useState<ContextType | 'all'>('all');
  const [filterSource, setFilterSource] = useState<ContextSource | 'all'>('all');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState<Record<string, any>>({});
  const queryClient = useQueryClient();

  const { data: contexts, isLoading } = useQuery({
    queryKey: ['contexts', filterType, filterStatus, filterSource],
    queryFn: () =>
      listContexts({
        type: filterType === 'all' ? undefined : filterType,
        status: filterStatus === 'all' ? undefined : filterStatus,
        source: filterSource === 'all' ? undefined : filterSource,
      }),
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

  const deleteMutation = useMutation({
    mutationFn: deleteContext,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contexts'] });
      toast.success('Context deleted');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, update }: { id: string; update: any }) => updateContext(id, update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contexts'] });
      setEditingId(null);
      toast.success('Context updated');
    },
  });

  const handleEdit = (context: ContextObject) => {
    setEditingId(context.id);
    setEditContent(context.content);
  };

  const handleSaveEdit = (id: string) => {
    updateMutation.mutate({ id, update: { content: editContent } });
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditContent({});
  };

  const handleDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this context?')) {
      deleteMutation.mutate(id);
    }
  };

  // Group contexts by type
  const groupedContexts: Record<string, ContextObject[]> = {};
  contexts?.forEach((context) => {
    if (!groupedContexts[context.type]) {
      groupedContexts[context.type] = [];
    }
    groupedContexts[context.type].push(context);
  });

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">Context Management</h1>
          <p className="text-sm text-muted-foreground">
            Review and manage your business context
          </p>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        {/* Filters */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Filter className="h-5 w-5" />
              Filters
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Status</label>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value as any)}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="all">All</option>
                  <option value="pending">Pending</option>
                  <option value="confirmed">Confirmed</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Type</label>
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value as any)}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="all">All</option>
                  <option value="company">Company</option>
                  <option value="industry">Industry</option>
                  <option value="regulation">Regulation</option>
                  <option value="competitor">Competitor</option>
                  <option value="persona">Persona</option>
                  <option value="assumption">Assumption</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Source</label>
                <select
                  value={filterSource}
                  onChange={(e) => setFilterSource(e.target.value as any)}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="all">All</option>
                  <option value="external">External</option>
                  <option value="inferred">Inferred</option>
                  <option value="user">User</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Context List */}
        {isLoading ? (
          <div className="text-center py-12">Loading contexts...</div>
        ) : !contexts || contexts.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <p className="text-muted-foreground">No context objects found</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
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
                        ({items.length})
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
                                      setEditContent(JSON.parse(e.target.value));
                                    } catch (err) {
                                      // Invalid JSON
                                    }
                                  }}
                                  className="w-full p-2 border rounded font-mono text-sm"
                                  rows={8}
                                />
                                <div className="flex gap-2">
                                  <Button
                                    size="sm"
                                    onClick={() => handleSaveEdit(context.id)}
                                    disabled={updateMutation.isPending}
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
                                  <span className="capitalize">Status: {context.status}</span>
                                  <span className="capitalize">Source: {context.source}</span>
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
                          {editingId !== context.id && (
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleEdit(context)}
                                title="Edit"
                              >
                                <Edit2 className="h-4 w-4" />
                              </Button>
                              {context.status !== 'confirmed' && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => confirmMutation.mutate(context.id)}
                                  disabled={confirmMutation.isPending}
                                  className="text-green-600 hover:text-green-700"
                                  title="Confirm"
                                >
                                  <Check className="h-4 w-4" />
                                </Button>
                              )}
                              {context.status !== 'rejected' && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => rejectMutation.mutate(context.id)}
                                  disabled={rejectMutation.isPending}
                                  className="text-orange-600 hover:text-orange-700"
                                  title="Reject"
                                >
                                  <X className="h-4 w-4" />
                                </Button>
                              )}
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleDelete(context.id)}
                                disabled={deleteMutation.isPending}
                                className="text-red-600 hover:text-red-700"
                                title="Delete"
                              >
                                <Trash2 className="h-4 w-4" />
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
          </div>
        )}
      </div>
    </div>
  );
}
