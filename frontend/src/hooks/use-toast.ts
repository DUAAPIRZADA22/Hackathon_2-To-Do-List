/**
 * Toast notification hook
 * Uses sonner for toast notifications
 */

import { toast } from 'sonner';

export interface ToastOptions {
  title?: string;
  description?: string;
  variant?: 'info' | 'success' | 'warning' | 'error';
  duration?: number;
}

export function useToast() {
  const showToast = ({
    title,
    description,
    variant = 'info',
    duration = 4000
  }: ToastOptions) => {
    switch (variant) {
      case 'success':
        toast.success(title, { description, duration });
        break;
      case 'error':
        toast.error(title, { description, duration });
        break;
      case 'warning':
        toast.warning(title, { description, duration });
        break;
      default:
        toast.info(title, { description, duration });
    }
  };

  return {
    toast: showToast,
    success: (title: string, description?: string) =>
      showToast({ title, description, variant: 'success' }),
    error: (title: string, description?: string) =>
      showToast({ title, description, variant: 'error' }),
    warning: (title: string, description?: string) =>
      showToast({ title, description, variant: 'warning' }),
    info: (title: string, description?: string) =>
      showToast({ title, description, variant: 'info' })
  };
}
