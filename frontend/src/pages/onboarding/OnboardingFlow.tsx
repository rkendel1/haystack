import { useState } from 'react';
import CompanyInfoStep from './CompanyInfoStep';
import ContextDiscovery from './ContextDiscovery';
import ContextReview from './ContextReview';

type OnboardingStep = 'company_info' | 'discovery' | 'review' | 'complete';

export default function OnboardingFlow() {
  const [currentStep, setCurrentStep] = useState<OnboardingStep>('company_info');
  const [sessionId, setSessionId] = useState<string>('');

  const handleCompanyInfoComplete = (newSessionId: string) => {
    setSessionId(newSessionId);
    setCurrentStep('discovery');
  };

  const handleDiscoveryComplete = () => {
    setCurrentStep('review');
  };

  const handleReviewComplete = () => {
    setCurrentStep('complete');
    // Redirect to main app
    window.location.href = '/';
  };

  if (currentStep === 'company_info') {
    return <CompanyInfoStep onComplete={handleCompanyInfoComplete} />;
  }

  if (currentStep === 'discovery') {
    return <ContextDiscovery sessionId={sessionId} onComplete={handleDiscoveryComplete} />;
  }

  if (currentStep === 'review') {
    return <ContextReview sessionId={sessionId} onComplete={handleReviewComplete} />;
  }

  if (currentStep === 'complete') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-4">Onboarding Complete!</h1>
          <p className="text-muted-foreground">Redirecting to your dashboard...</p>
        </div>
      </div>
    );
  }

  return null;
}
