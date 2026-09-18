import { useState } from 'react';
import {
  Menu, X, ArrowRight, CheckCircle2, Bot, FileSpreadsheet, Receipt, LayoutDashboard,
  ShieldCheck, Sparkles
} from 'lucide-react';
import './App.css';

const APP_URL = '/app';

function Logo() {
  return (
    <div className="logo-mark">
      <div className="logo-mark-icon">Q</div>
      <span className="logo-mark-text">Quanta</span>
    </div>
  );
}

const SERVICIOS = [
  {
    icon: <Bot size={22} />,
    title: 'Sincronización automática con SUNAT',
    desc: 'Un bot descarga y ordena tus comprobantes de compras y ventas desde el SIRE, sin que tengas que entrar tú mismo al portal.',
  },
  {
    icon: <Sparkles size={22} />,
    title: 'Procesamiento con Inteligencia Artificial',
    desc: 'Clasificación contable automática, extracción de glosas desde los XML y validación de comprobantes antes del cierre.',
  },
  {
    icon: <Receipt size={22} />,
    title: 'Facturación electrónica integrada',
    desc: 'Emite comprobantes directamente desde la plataforma, conectados al mismo registro contable de tu empresa.',
  },
  {
    icon: <LayoutDashboard size={22} />,
    title: 'Dashboard financiero en tiempo real',
    desc: 'Ventas, compras, IGV resultante y alertas de documentos observados, siempre actualizados por periodo.',
  },
];

const PLANES = [
  {
    name: 'Básico',
    desc: 'Para independientes y negocios chicos',
    price: 'S/ 150',
    featured: false,
    features: ['1 RUC', 'Sincronización SUNAT mensual', 'Dashboard financiero', 'Soporte por correo'],
  },
  {
    name: 'Profesional',
    desc: 'El más elegido por estudios contables',
    price: 'S/ 350',
    featured: true,
    features: ['Hasta 5 RUC', 'Sincronización SUNAT diaria', 'Procesamiento IA + clasificación', 'Facturación electrónica', 'Soporte prioritario'],
  },
  {
    name: 'Empresa',
    desc: 'Para carteras grandes de clientes',
    price: 'A medida',
    featured: false,
    features: ['RUC ilimitados', 'Todo lo del plan Profesional', 'Onboarding dedicado', 'Soporte dedicado'],
  },
];

const TESTIMONIOS = [
  {
    quote: 'Desde que automatizamos la sincronización con SUNAT, el cierre mensual nos toma una fracción del tiempo que tomaba antes.',
    name: 'Nombre Apellido',
    role: 'Gerente General — Empresa',
  },
  {
    quote: 'El dashboard nos da visibilidad real de cada cliente sin tener que armar reportes a mano cada vez.',
    name: 'Nombre Apellido',
    role: 'Contador — Estudio',
  },
  {
    quote: 'La clasificación con IA redujo muchísimo el trabajo manual de revisar comprobante por comprobante.',
    name: 'Nombre Apellido',
    role: 'Cargo — Empresa',
  },
];

const STATS = [
  { value: '100+', label: 'Clientes activos' },
  { value: '95%', label: 'Automatización del proceso' },
  { value: '24/7', label: 'Sincronización con SUNAT' },
  { value: '3', label: 'Años de trayectoria' },
];

export default function App() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <>
      <header className="site-header">
        <div className="container">
          <a href="#top" className="header-logo">
            <Logo />
          </a>

          <nav className="header-nav">
            <a href="#servicios">Servicios</a>
            <a href="#precios">Precios</a>
            <a href="#testimonios">Testimonios</a>
            <a href="#nosotros">Nosotros</a>
          </nav>

          <div className="header-actions">
            <a href={APP_URL} className="btn btn-primary btn-sm">
              Ingresar <ArrowRight size={15} />
            </a>
            <button className="nav-toggle" onClick={() => setMenuOpen(!menuOpen)} aria-label="Abrir menú">
              {menuOpen ? <X size={22} /> : <Menu size={22} />}
            </button>
          </div>
        </div>

        {menuOpen && (
          <div className="container" style={{paddingTop: '1rem', paddingBottom: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem'}}>
            <a href="#servicios" onClick={() => setMenuOpen(false)}>Servicios</a>
            <a href="#precios" onClick={() => setMenuOpen(false)}>Precios</a>
            <a href="#testimonios" onClick={() => setMenuOpen(false)}>Testimonios</a>
            <a href="#nosotros" onClick={() => setMenuOpen(false)}>Nosotros</a>
          </div>
        )}
      </header>

      <main id="top">
        {/* HERO */}
        <section className="hero">
          <div className="hero-aurora">
            <span className="hero-blob b1"></span>
            <span className="hero-blob b2"></span>
            <span className="hero-blob b3"></span>
          </div>
          <div className="container">
            <div className="hero-content">
              <div className="eyebrow"><Sparkles size={13} /> IA para tu estudio contable</div>
              <h1 className="hero-title">
                Contabilidad automatizada, <span className="gradient-text">sin perseguir a SUNAT</span>
              </h1>
              <p className="hero-subtitle">
                Quanta sincroniza tus comprobantes de compras y ventas directo desde SUNAT, los procesa con
                inteligencia artificial y te entrega un dashboard financiero listo para cada cierre.
              </p>
              <div className="hero-ctas">
                <a href={APP_URL} className="btn btn-primary">Ingresar a la plataforma <ArrowRight size={16} /></a>
                <a href="#servicios" className="btn btn-outline">Conocer los servicios</a>
              </div>
              <div className="hero-trust">
                <div className="avatars">
                  <img src="https://i.pravatar.cc/100?img=11" alt="" />
                  <img src="https://i.pravatar.cc/100?img=12" alt="" />
                  <img src="https://i.pravatar.cc/100?img=13" alt="" />
                </div>
                <span>Más de 100 clientes ya automatizan su contabilidad con Quanta</span>
              </div>
            </div>
          </div>
        </section>

        {/* SERVICIOS */}
        <section id="servicios" className="section">
          <div className="container">
            <div className="section-header">
              <div className="eyebrow">Servicios</div>
              <h2 className="section-title">Todo el flujo contable, en un solo lugar</h2>
              <p className="section-subtitle">Desde la sincronización con SUNAT hasta el reporte final del periodo.</p>
            </div>
            <div className="servicios-grid">
              {SERVICIOS.map((s, i) => (
                <div key={i} className="card servicio-card">
                  <div className="section-icon">{s.icon}</div>
                  <h3>{s.title}</h3>
                  <p>{s.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* PRECIOS */}
        <section id="precios" className="section">
          <div className="container">
            <div className="section-header">
              <div className="eyebrow">Precios</div>
              <h2 className="section-title">
                Planes para cada tamaño de estudio
              </h2>
              <p className="section-subtitle">
                Precios referenciales — se ajustan según la cantidad de RUC y el volumen de comprobantes.
              </p>
            </div>
            <div className="pricing-grid">
              {PLANES.map((p, i) => (
                <div key={i} className={`card pricing-card ${p.featured ? 'featured' : ''}`}>
                  {p.featured && <div className="pricing-badge">Más elegido</div>}
                  <div className="pricing-plan-name">{p.name}</div>
                  <div className="pricing-plan-desc">{p.desc}</div>
                  <div className="pricing-price">
                    <span className="amount">{p.price}</span>
                    {p.price.startsWith('S/') && <span className="period">/ mes</span>}
                  </div>
                  <ul className="pricing-features">
                    {p.features.map((f, j) => (
                      <li key={j}><CheckCircle2 size={16} /> {f}</li>
                    ))}
                  </ul>
                  <a href={APP_URL} className={`btn ${p.featured ? 'btn-primary' : 'btn-outline'}`}>Empezar</a>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* TESTIMONIOS */}
        <section id="testimonios" className="section">
          <div className="container">
            <div className="section-header">
              <div className="eyebrow">Testimonios</div>
              <h2 className="section-title">Lo que dicen quienes ya lo usan</h2>
            </div>
            <div className="testimonios-grid">
              {TESTIMONIOS.map((t, i) => (
                <div key={i} className="card testimonio-card">
                  <p className="testimonio-quote">"{t.quote}"</p>
                  <div className="testimonio-author">
                    <div className="testimonio-avatar">{t.name.split(' ').map(w => w[0]).join('')}</div>
                    <div>
                      <div className="testimonio-name">{t.name}</div>
                      <div className="testimonio-role">{t.role}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* NOSOTROS */}
        <section id="nosotros" className="section">
          <div className="container">
            <div className="nosotros-grid">
              <div className="nosotros-copy">
                <div className="eyebrow"><ShieldCheck size={13} /> Nosotros</div>
                <h2 className="section-title">Un estudio contable que automatiza lo repetitivo para enfocarse en lo que importa</h2>
                <p>
                  Quanta Contadores nació para resolver un problema concreto: demasiadas horas perdidas
                  descargando comprobantes de SUNAT y clasificándolos a mano. Construimos nuestra propia
                  plataforma de automatización e IA para que cada cierre sea más rápido y confiable, tanto
                  para nuestro equipo como para nuestros clientes.
                </p>
              </div>
              <div className="stats-grid">
                {STATS.map((s, i) => (
                  <div key={i} className="card stat-card">
                    <div className="stat-value">{s.value}</div>
                    <div className="stat-label">{s.label}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* CTA FINAL */}
        <section className="section">
          <div className="container">
            <div className="cta-final">
              <h2 className="section-title" style={{margin: '0 auto 1rem', textAlign: 'center'}}>
                Lleva la contabilidad de tu empresa al siguiente nivel
              </h2>
              <p className="section-subtitle" style={{margin: '0 auto 2rem', textAlign: 'center'}}>
                Ingresá a la plataforma con tu RUC y Clave SOL, o contactanos para conocer más.
              </p>
              <a href={APP_URL} className="btn btn-primary">Ingresar a Quanta <ArrowRight size={16} /></a>
            </div>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="container">
          <div className="footer-top">
            <div className="footer-logo">
              <Logo />
            </div>
            <div className="footer-links">
              <div className="footer-col">
                <h4>Producto</h4>
                <a href="#servicios">Servicios</a>
                <a href="#precios">Precios</a>
                <a href={APP_URL}>Ingresar</a>
              </div>
              <div className="footer-col">
                <h4>Contacto</h4>
                <span>contacto@quantacontadores.pe</span>
                <span>+51 900 000 000</span>
              </div>
            </div>
          </div>
          <div className="footer-bottom">
            © {new Date().getFullYear()} Quanta Contadores. Todos los derechos reservados.
          </div>
        </div>
      </footer>
    </>
  );
}
