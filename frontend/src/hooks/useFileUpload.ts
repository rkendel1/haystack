import { useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import { UploadResponse } from '@/types';

export const useFileUpload = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      
      const { data } = await api.post<UploadResponse>('/index', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return data;
    },
    onSuccess: () => {
      // Invalidate documents query to refresh the list
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
};
