import React, { ReactNode, useEffect } from 'react'
import { X } from 'lucide-react'
import clsx from 'clsx'
import { createPortal } from 'react-dom'

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children, size = 'md' }) => {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    if (isOpen) {
      document.body.style.overflow = 'hidden'
      window.addEventListener('keydown', handleEscape)
    }
    return () => {
      document.body.style.overflow = 'unset'
      window.removeEventListener('keydown', handleEscape)
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  }

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-bg-base/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className={clsx(
          "w-full bg-bg-surface border border-border rounded-lg shadow-2xl flex flex-col max-h-[90vh] animate-in zoom-in-95 duration-200",
          sizes[size]
        )}
      >
        <div className="flex items-center justify-between p-6 border-b border-border">
          <h3 className="text-xl font-syne font-extrabold text-accent uppercase tracking-tight">{title}</h3>
          <button 
            onClick={onClose}
            className="text-muted hover:text-text transition-colors p-1"
          >
            <X size={24} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-6 font-mono text-sm">
          {children}
        </div>
      </div>
    </div>,
    document.body
  )
}

export default Modal
