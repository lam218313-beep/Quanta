import { useState } from 'react'
import { supabase } from '../supabaseClient'
import { Mail, Lock, Loader2, AlertCircle, Eye, EyeOff, IdCard, Shield, Building2 } from 'lucide-react'
import './LoginView.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://quanta-production-07d7.up.railway.app'

export default function LoginView({ onLoginSuccess }) {
  const [mode, setMode] = useState('staff') // 'staff' | 'client'

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const [ruc, setRuc] = useState('')
  const [claveSol, setClaveSol] = useState('')

  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleStaffLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const { data, error: authError } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (authError) throw authError

      // Fetch user profile to ensure they are active
      const { data: profileData, error: profileError } = await supabase
        .from('user_profiles')
        .select('activo, role')
        .eq('id', data.user.id)
        .single()

      if (profileError) {
        console.error("Profile error:", profileError)
      } else if (profileData && !profileData.activo) {
        await supabase.auth.signOut()
        throw new Error('Tu cuenta ha sido desactivada. Contacta al administrador.')
      }

      if (onLoginSuccess) onLoginSuccess(data.session)

    } catch (err) {
      setError(err.message || 'Credenciales incorrectas')
    } finally {
      setLoading(false)
    }
  }

  const handleClientLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const res = await fetch(`${API_BASE_URL}/api/auth/client-login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ruc, clave_sol: claveSol })
      })

      const body = await res.json()
      if (!res.ok) throw new Error(body.detail || 'RUC o clave SOL incorrectos')

      const { error: setSessionError, data } = await supabase.auth.setSession({
        access_token: body.access_token,
        refresh_token: body.refresh_token,
      })
      if (setSessionError) throw setSessionError

      if (onLoginSuccess) onLoginSuccess(data.session)

    } catch (err) {
      setError(err.message || 'RUC o clave SOL incorrectos')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-wrapper">
      <div className="aurora-bg">
        <span className="aurora-blob b1"></span>
        <span className="aurora-blob b2"></span>
        <span className="aurora-blob b3"></span>
      </div>

      <div className="login-container-new">

        {/* Left Side: Visual / Abstract */}
        <div className="login-left-pane">
          <div className="left-pane-content">
            <h1 className="smart-ai-title">QUANTA</h1>
            <h1 className="smart-ai-title outline">CONTABILIDAD</h1>
            
            <div className="left-pane-bottom">
              <h2>IA para tu Estudio Contable</h2>
              <p>Experimenta un procesamiento más inteligente con automatización impulsada por IA, análisis precisos y productividad impecable en cada cierre.</p>
            </div>
          </div>
        </div>

        {/* Right Side: Form */}
        <div className="login-right-pane">
          <div className="form-wrapper">
            <div className="login-header-new">
              <div className="logo-icon-new">
                <span>Q</span>
              </div>
              <h2>Bienvenido de nuevo</h2>
              <p>{mode === 'staff' ? 'Inicia sesión para acceder a tu plataforma' : 'Ingresa con el RUC y la Clave SOL de tu empresa'}</p>
            </div>

            <div className="login-mode-switch">
              <button
                type="button"
                className={mode === 'staff' ? 'active' : ''}
                onClick={() => { setMode('staff'); setError(null) }}
              >
                <Shield size={15} /> Contador / Admin
              </button>
              <button
                type="button"
                className={mode === 'client' ? 'active' : ''}
                onClick={() => { setMode('client'); setError(null) }}
              >
                <Building2 size={15} /> Cliente
              </button>
            </div>

            {error && (
              <div className="login-error-new">
                <AlertCircle size={16} />
                <span>{error}</span>
              </div>
            )}

            {mode === 'staff' ? (
              <form onSubmit={handleStaffLogin} className="login-form-new">
                <div className="input-group-new">
                  <label>Correo Electrónico</label>
                  <div className="input-wrapper-new">
                    <Mail className="input-icon-new" size={18} />
                    <input
                      type="email"
                      placeholder="tu@correo.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="input-group-new">
                  <label>Contraseña</label>
                  <div className="input-wrapper-new">
                    <Lock className="input-icon-new" size={18} />
                    <input
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                    <button
                      type="button"
                      className="toggle-password"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <div className="form-options">
                  <label className="remember-me">
                    <input type="checkbox" />
                    <span>Recordarme</span>
                  </label>
                </div>

                <button type="submit" className="submit-btn" disabled={loading}>
                  {loading ? <Loader2 className="spin" size={20} /> : "Iniciar Sesión"}
                </button>
              </form>
            ) : (
              <form onSubmit={handleClientLogin} className="login-form-new">
                <div className="input-group-new">
                  <label>RUC</label>
                  <div className="input-wrapper-new">
                    <IdCard className="input-icon-new" size={18} />
                    <input
                      type="text"
                      placeholder="Correo o usuario"
                      value={ruc}
                      onChange={(e) => setRuc(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="input-group-new">
                  <label>Clave SOL</label>
                  <div className="input-wrapper-new">
                    <Lock className="input-icon-new" size={18} />
                    <input
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••"
                      value={claveSol}
                      onChange={(e) => setClaveSol(e.target.value)}
                      required
                    />
                    <button
                      type="button"
                      className="toggle-password"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <div className="form-options">
                  <span style={{fontSize: '0.78rem', color: '#64748b'}}>La misma clave que usás para ingresar a SUNAT SOL.</span>
                </div>

                <button type="submit" className="submit-btn" disabled={loading}>
                  {loading ? <Loader2 className="spin" size={20} /> : "Iniciar Sesión"}
                </button>
              </form>
            )}
          </div>
          
          {/* Social Proof Box */}
          <div className="social-proof-box">
            <div className="avatars">
              <img src="https://i.pravatar.cc/100?img=11" alt="User" />
              <img src="https://i.pravatar.cc/100?img=12" alt="User" />
              <img src="https://i.pravatar.cc/100?img=13" alt="User" />
            </div>
            <div className="social-text">
              <h4>Más de 100 clientes</h4>
              <span>Quanta</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
