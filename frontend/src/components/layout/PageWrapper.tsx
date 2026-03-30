import React, { ReactNode } from 'react'
import Sidebar from './Sidebar'
import TopBar from './TopBar'

interface PageWrapperProps {
  children: ReactNode;
  title: string;
}

const PageWrapper: React.FC<PageWrapperProps> = ({ children, title }) => {
  return (
    <div className="flex min-h-screen bg-bg-base text-text">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <TopBar title={title} />
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

export default PageWrapper
