import React from 'react'
import { Bell, Search } from 'lucide-react'

interface TopBarProps {
  title: string;
}

const TopBar: React.FC<TopBarProps> = ({ title }) => {
  return (
    <header className="h-14 bg-bg-surface border-b border-border px-6 flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <h2 className="text-xl font-syne font-extrabold">{title}</h2>
      </div>

      <div className="flex items-center space-x-6">
        <div className="relative group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted group-focus-within:text-accent transition-colors" size={18} />
          <input 
            type="text" 
            placeholder="Cmd + K to search" 
            className="bg-bg-base border border-border rounded-md pl-10 pr-4 py-1.5 text-sm font-mono focus:outline-none focus:border-accent transition-all w-64"
          />
        </div>

        <button className="relative text-muted hover:text-text transition-colors">
          <Bell size={20} />
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-accent text-[10px] text-white flex items-center justify-center rounded-full font-bold">
            3
          </span>
        </button>
      </div>
    </header>
  )
}

export default TopBar
