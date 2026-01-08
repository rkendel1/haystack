import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { useFileUpload } from '@/hooks/useFileUpload';
import { Card, CardContent } from '@/components/ui/card';
import { Upload, File, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

export default function FileUploader() {
  const { mutate: uploadFile, isPending } = useFileUpload();
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploadStatus('idle');

    uploadFile(file, {
      onSuccess: (data) => {
        setUploadStatus('success');
        toast.success(`File uploaded successfully: ${data.file_name}`);
        setTimeout(() => setUploadStatus('idle'), 3000);
      },
      onError: (error) => {
        setUploadStatus('error');
        toast.error(`Upload failed: ${error.message}`);
        setTimeout(() => setUploadStatus('idle'), 3000);
      },
    });
  }, [uploadFile]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
    multiple: false,
    disabled: isPending,
  });

  return (
    <Card>
      <CardContent className="p-6">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-primary bg-primary/10'
              : 'border-border hover:border-primary/50'
          } ${isPending ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center gap-3">
            {isPending ? (
              <Loader2 className="h-12 w-12 text-primary animate-spin" />
            ) : uploadStatus === 'success' ? (
              <CheckCircle className="h-12 w-12 text-green-500" />
            ) : uploadStatus === 'error' ? (
              <XCircle className="h-12 w-12 text-destructive" />
            ) : isDragActive ? (
              <Upload className="h-12 w-12 text-primary" />
            ) : (
              <File className="h-12 w-12 text-muted-foreground" />
            )}
            <div>
              <p className="text-sm font-medium">
                {isPending
                  ? 'Uploading...'
                  : uploadStatus === 'success'
                  ? 'Upload successful!'
                  : uploadStatus === 'error'
                  ? 'Upload failed'
                  : isDragActive
                  ? 'Drop file here'
                  : 'Drag & drop file here, or click to select'}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Supports PDF, TXT, MD files
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
