import { useState } from 'react'
import { supabase } from '../supabaseClient'
import { Mail, Lock, Loader2, AlertCircle, Eye, EyeOff } from 'lucide-react'
import './LoginView.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://quanta-production-07d7.up.railway.app'

export default function LoginView({ onLoginSuccess }) {
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const loginAsStaff = async () => {
    const { data, error: authError } = await supabase.auth.signInWithPassword({
      email: identifier,
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

    return data.session
  }

  const loginAsClient = async () => {
    const res = await fetch(`${API_BASE_URL}/api/auth/client-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ruc: identifier, clave_sol: password })
    })

    const body = await res.json()
    if (!res.ok) throw new Error(body.detail || 'Usuario o contraseña incorrectos')

    const { error: setSessionError, data } = await supabase.auth.setSession({
      access_token: body.access_token,
      refresh_token: body.refresh_token,
    })
    if (setSessionError) throw setSessionError

    return data.session
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const session = identifier.includes('@')
        ? await loginAsStaff()
        : await loginAsClient()

      if (onLoginSuccess) onLoginSuccess(session)

    } catch (err) {
      setError(err.message || 'Usuario o contraseña incorrectos')
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
            <img src="/logo-quanta.png" alt="Quanta Contadores" className="left-pane-logo" />

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
              <img src="/logo-quanta.png" alt="Quanta Contadores" className="logo-icon-new-img" />
              <h2>Bienvenido de nuevo</h2>
              <p>Inicia sesión para acceder a tu plataforma</p>
            </div>

            {error && (
              <div className="login-error-new">
                <AlertCircle size={16} />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleLogin} className="login-form-new">
              <div className="input-group-new">
                <label>Usuario</label>
                <div className="input-wrapper-new">
                  <Mail className="input-icon-new" size={18} />
                  <input
                    type="text"
                    placeholder="Usuario o tu@correo.com"
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
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
