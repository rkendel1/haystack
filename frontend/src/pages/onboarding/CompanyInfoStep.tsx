import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { startOnboarding } from '@/lib/contextApi';
import { CompanyInfo } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Building2, Globe } from 'lucide-react';

interface CompanyInfoStepProps {
  onComplete: (sessionId: string) => void;
}

export default function CompanyInfoStep({ onComplete }: CompanyInfoStepProps) {
  const [formData, setFormData] = useState<CompanyInfo>({
    name: '',
    website: '',
    industry: '',
  });

  const startMutation = useMutation({
    mutationFn: (data: CompanyInfo) => startOnboarding(data),
    onSuccess: (session) => {
      onComplete(session.id);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    startMutation.mutate(formData);
  };

  const isValid = formData.name.trim() && formData.website.trim();

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
            <Building2 className="h-8 w-8 text-primary" />
          </div>
          <CardTitle className="text-3xl">Welcome to Haystack</CardTitle>
          <CardContent className="text-lg mt-2 p-0">
            Let's start by learning about your company. We'll discover relevant context to help you get started.
          </CardContent>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="company-name" className="block text-sm font-medium mb-2">
                Company Name *
              </label>
              <div className="relative">
                <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  id="company-name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full pl-10 pr-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="Acme Corporation"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="website" className="block text-sm font-medium mb-2">
                Company Website *
              </label>
              <div className="relative">
                <Globe className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  id="website"
                  type="url"
                  value={formData.website}
                  onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                  className="w-full pl-10 pr-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="https://acme.com"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="industry" className="block text-sm font-medium mb-2">
                Industry <span className="text-muted-foreground">(optional)</span>
              </label>
              <input
                id="industry"
                type="text"
                value={formData.industry}
                onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Technology, Healthcare, Finance, etc."
              />
              <p className="mt-1 text-sm text-muted-foreground">
                We'll auto-detect if not provided
              </p>
            </div>

            <Button
              type="submit"
              className="w-full"
              size="lg"
              disabled={!isValid || startMutation.isPending}
            >
              {startMutation.isPending ? 'Starting Discovery...' : 'Continue'}
            </Button>
          </form>

          {startMutation.isError && (
            <div className="mt-4 p-4 bg-destructive/10 text-destructive rounded-md text-sm">
              {(startMutation.error as Error).message || 'Failed to start onboarding. Please try again.'}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
