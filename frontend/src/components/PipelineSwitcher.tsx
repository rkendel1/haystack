import { PipelineMode } from '@/types';

interface PipelineSwitcherProps {
  value: PipelineMode;
  onChange: (value: PipelineMode) => void;
}

export default function PipelineSwitcher({ value, onChange }: PipelineSwitcherProps) {
  const pipelines: { value: PipelineMode; label: string; description: string }[] = [
    {
      value: 'rag',
      label: 'RAG',
      description: 'Retrieval-Augmented Generation',
    },
    {
      value: 'agent',
      label: 'Agent',
      description: 'Step-by-step reasoning',
    },
    {
      value: 'search',
      label: 'Search',
      description: 'Semantic search only',
    },
  ];

  return (
    <div className="flex gap-2">
      {pipelines.map((pipeline) => (
        <button
          key={pipeline.value}
          onClick={() => onChange(pipeline.value)}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            value === pipeline.value
              ? 'bg-primary text-primary-foreground'
              : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
          }`}
          title={pipeline.description}
        >
          {pipeline.label}
        </button>
      ))}
    </div>
  );
}
