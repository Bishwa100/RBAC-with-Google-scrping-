import React from 'react'
import { Snowflake, Unlock } from 'lucide-react'
import Badge from '../ui/Badge'

interface FrozenBadgeProps {
  isFrozen: boolean;
}

const FrozenBadge: React.FC<FrozenBadgeProps> = ({ isFrozen }) => {
  if (!isFrozen) {
    return (
      <Badge variant="success" className="space-x-1">
        <Unlock size={10} />
        <span>UNFROZEN</span>
      </Badge>
    )
  }

  return (
    <Badge variant="frozen" className="space-x-1 border-frozen/30 shadow-[0_0_8px_rgba(91,207,255,0.2)]">
      <Snowflake size={10} className="animate-spin-slow" />
      <span>FROZEN_PROTOCOL</span>
    </Badge>
  )
}

export default FrozenBadge
