import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { login } from '../api/auth'
import { useAuthStore } from '../store/authStore'
import { Shield, Lock, Mail, Loader2 } from 'lucide-react'

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
})

type LoginForm = z.infer<typeof loginSchema>

const Login: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false)
  const setAuth = useAuthStore(state => state.setAuth)
  const navigate = useNavigate()

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema)
  })

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true)
    try {
      const response = await login(data)
      const { user, access_token, refresh_token } = response.data
      
      setAuth(user, access_token, refresh_token)
      toast.success('Login successful')
      
      const minLevel = Math.min(...user.roles.map(r => r.level))
      if (minLevel === 0) navigate('/dashboard')
      else if (minLevel <= 1) navigate('/dept-dashboard')
      else navigate('/records')
      
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-bg-base">
      {/* Left Side - Display */}
      <div className="hidden lg:flex flex-col justify-center p-12 bg-bg-surface relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-accent/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-accent2/5 rounded-full translate-y-1/2 -translate-x-1/2 blur-3xl"></div>
        
        <div className="relative z-10">
          <div className="flex items-center space-x-3 text-accent mb-8">
            <Shield size={48} strokeWidth={2.5} />
            <h1 className="text-4xl font-syne font-extrabold tracking-tighter">RBAC<br/>SYSTEM</h1>
          </div>
          
          <h2 className="text-6xl font-syne font-extrabold text-text mb-6 leading-tight">
            SECURE<br/>COMMAND<br/>CENTER.
          </h2>
          
          <p className="text-muted text-xl font-mono max-w-md">
            Advanced multi-tenant role-based access control with frozen-data protocols and multi-stage approval workflows.
          </p>
        </div>

        <div className="absolute bottom-12 left-12 flex space-x-6 text-dim font-mono text-sm">
          <div>// ACCESS_LEVEL: RESTRICTED</div>
          <div>// PROTOCOL: AES-256</div>
        </div>
      </div>

      {/* Right Side - Form */}
      <div className="flex flex-col justify-center items-center p-8">
        <div className="w-full max-w-md space-y-8">
          <div className="text-center lg:text-left">
            <h3 className="text-3xl font-syne font-extrabold mb-2">AUTHENTICATE</h3>
            <p className="text-muted font-mono">Enter your credentials to access the terminal</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="space-y-2">
              <label className="text-xs font-mono text-muted uppercase tracking-widest block" htmlFor="username">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-dim" size={18} />
                <input
                  {...register('email')}
                  type="email"
                  className={`w-full bg-bg-surface border ${errors.email ? 'border-danger' : 'border-border'} rounded-md pl-10 pr-4 py-3 font-mono focus:outline-none focus:border-accent transition-colors`}
                  placeholder="admin@system.com"
                />
              </div>
              {errors.email && <p className="text-danger text-xs font-mono mt-1">{errors.email.message}</p>}
            </div>

            <div className="space-y-2">
              <label className="text-xs font-mono text-muted uppercase tracking-widest block" htmlFor="password">
                Security Key
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-dim" size={18} />
                <input
                  {...register('password')}
                  type="password"
                  className={`w-full bg-bg-surface border ${errors.password ? 'border-danger' : 'border-border'} rounded-md pl-10 pr-4 py-3 font-mono focus:outline-none focus:border-accent transition-colors`}
                  placeholder="••••••••••••"
                />
              </div>
              {errors.password && <p className="text-danger text-xs font-mono mt-1">{errors.password.message}</p>}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-accent hover:bg-accent/90 disabled:opacity-50 text-white font-syne font-extrabold py-4 rounded-md transition-all flex items-center justify-center space-x-2 group"
            >
              {isLoading ? (
                <Loader2 className="animate-spin" size={20} />
              ) : (
                <>
                  <span>INITIALIZE SESSION</span>
                  <Shield size={18} className="group-hover:scale-110 transition-transform" />
                </>
              )}
            </button>
          </form>

          <div className="pt-8 border-t border-border/50 text-center">
            <p className="text-dim font-mono text-xs">
              UNAUTHORIZED ACCESS IS STRICTLY LOGGED AND MONITORED.<br/>
              SESSION TIMEOUT: 60 MINUTES.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
