import React from 'react'
import clsx from 'clsx'

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'frozen' | 'muted';
  className?: string;
}

const Badge: React.FC<BadgeProps> = ({ children, variant = 'primary', className }) => {
  const variants = {
    primary: 'bg-accent/10 text-accent border-accent/20',
    secondary: 'bg-accent2/10 text-accent2 border-accent2/20',
    success: 'bg-success/10 text-success border-success/20',
    warning: 'bg-warning/10 text-warning border-warning/20',
    danger: 'bg-danger/10 text-danger border-danger/20',
    frozen: 'bg-frozen/10 text-frozen border-frozen/20',
    muted: 'bg-muted/10 text-muted border-muted/20',
  }

  return (
    <span className={clsx(
      "inline-flex items-center px-2 py-0.5 rounded border text-[10px] font-mono font-bold uppercase tracking-wider",
      variants[variant],
      className
    )}>
      {children}
    </span>
  )
}

export default Badge
