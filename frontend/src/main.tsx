import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import ConfirmProvider from './components/ui/ConfirmProvider'

// Fonts
import "@fontsource/syne/700.css";
import "@fontsource/syne/800.css";
import "@fontsource/dm-mono/400.css";
import "@fontsource/dm-mono/500.css";

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfirmProvider>
      <App />
    </ConfirmProvider>
  </React.StrictMode>,
)
