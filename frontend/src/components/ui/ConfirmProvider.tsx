import React, { createContext, ReactNode, useCallback, useContext, useState } from 'react'
import Modal from './Modal'
import Button from './Button'

type ConfirmFn = (message?: string, title?: string) => Promise<boolean>

const ConfirmContext = createContext<ConfirmFn | null>(null)

export const ConfirmProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [title, setTitle] = useState('Confirm')
  const [resolver, setResolver] = useState<((value: boolean) => void) | null>(null)

  const confirm: ConfirmFn = useCallback((msg = 'Are you sure?', ttl = 'Confirm') => {
    return new Promise<boolean>((resolve) => {
      setMessage(msg)
      setTitle(ttl)
      setIsOpen(true)
      setResolver(() => resolve)
    })
  }, [])

  const handleClose = (result: boolean) => {
    setIsOpen(false)
    if (resolver) resolver(result)
    setResolver(null)
  }

  return (
    <ConfirmContext.Provider value={confirm}>
      {children}

      <Modal isOpen={isOpen} onClose={() => handleClose(false)} title={title} size="sm">
        <div className="space-y-4">
          <p className="font-mono text-sm text-text">{message}</p>
          <div className="flex space-x-3 pt-4">
            <Button variant="ghost" className="w-full" onClick={() => handleClose(false)}>Cancel</Button>
            <Button className="w-full" onClick={() => handleClose(true)}>Confirm</Button>
          </div>
        </div>
      </Modal>
    </ConfirmContext.Provider>
  )
}

export const useConfirm = (): ConfirmFn => {
  const ctx = useContext(ConfirmContext)
  if (!ctx) throw new Error('useConfirm must be used within a ConfirmProvider')
  return ctx
}

export default ConfirmProvider
