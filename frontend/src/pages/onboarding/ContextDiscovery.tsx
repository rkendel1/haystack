import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getOnboardingContext } from '@/lib/contextApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Sparkles, Building2, Scale, Users, TrendingUp, Shield, Lightbulb } from 'lucide-react';

interface ContextDiscoveryProps {
  sessionId: string;
  onComplete: () => void;
}

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  company: Building2,
  regulation: Scale,
  persona: Users,
  competitor: TrendingUp,
  industry: Shield,
  assumption: Lightbulb,
};

// Configuration constants for discovery thresholds
const MIN_CONTEXTS_FOR_COMPLETION = 5; // Minimum contexts needed before auto-advancing
const EXPECTED_TOTAL_CONTEXTS = 15; // Expected total contexts for progress calculation
const AUTO_ADVANCE_DELAY_MS = 1500; // Delay before auto-advancing after completion

export default function ContextDiscovery({ sessionId, onComplete }: ContextDiscoveryProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['onboarding-context', sessionId],
    queryFn: () => getOnboardingContext(sessionId),
    refetchInterval: 2000, // Poll every 2 seconds
    refetchIntervalInBackground: false,
  });

  // Auto-advance when discovery is complete
  useEffect(() => {
    if (data && data.contexts.length > 0 && data.progress.discovered >= MIN_CONTEXTS_FOR_COMPLETION) {
      // Wait a bit before advancing to show completion
      const timer = setTimeout(() => {
        onComplete();
      }, AUTO_ADVANCE_DELAY_MS);
      return () => clearTimeout(timer);
    }
  }, [data, onComplete]);

  const categories = data?.progress.categories || [];
  const discovered = data?.progress.discovered || 0;

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
            <Sparkles className="h-8 w-8 text-primary animate-pulse" />
          </div>
          <CardTitle className="text-3xl">Discovering Your Context</CardTitle>
          <p className="text-muted-foreground mt-2">
            We're gathering relevant business context based on your company information.
            This will only take a moment.
          </p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Progress */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Progress</span>
              <span className="font-medium">{discovered} insights discovered</span>
            </div>
            <div className="w-full bg-secondary rounded-full h-2 overflow-hidden">
              <div
                className="bg-primary h-full transition-all duration-500"
                style={{ width: `${Math.min((discovered / EXPECTED_TOTAL_CONTEXTS) * 100, 100)}%` }}
              />
            </div>
          </div>

          {/* Category indicators */}
          <div className="grid grid-cols-2 gap-4">
            {['company', 'regulation', 'persona', 'competitor', 'industry', 'assumption'].map((category) => {
              const Icon = CATEGORY_ICONS[category];
              const isDiscovered = categories.includes(category);

              return (
                <div
                  key={category}
                  className={`flex items-center gap-3 p-3 rounded-lg border transition-all ${
                    isDiscovered
                      ? 'bg-primary/5 border-primary/20'
                      : 'bg-secondary/50 border-border'
                  }`}
                >
                  <div
                    className={`h-10 w-10 rounded-full flex items-center justify-center ${
                      isDiscovered ? 'bg-primary/10' : 'bg-secondary'
                    }`}
                  >
                    <Icon
                      className={`h-5 w-5 ${
                        isDiscovered ? 'text-primary' : 'text-muted-foreground'
                      }`}
                    />
                  </div>
                  <div className="flex-1">
                    <div className="font-medium capitalize text-sm">
                      {category}
                    </div>
                    {isDiscovered && (
                      <div className="text-xs text-primary">Discovered</div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {isLoading && (
            <div className="text-center text-sm text-muted-foreground">
              <div className="flex items-center justify-center gap-2">
                <div className="h-2 w-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="h-2 w-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="h-2 w-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
