import { useEffect, useState, useRef } from 'react'
import { Activity, Database, CheckCircle, RefreshCcw, Search, BarChart3, UploadCloud, Terminal, Download, Edit2, X, Upload, ChevronRight, ChevronDown, ChevronUp, UserPlus, Settings, FileText, Calculator, Users, LogOut, CheckCircle2, XCircle, RefreshCw, BarChart2, Mail, Building2 } from 'lucide-react'
import { supabase } from './supabaseClient'
import './App.css'
import FacturacionView from './components/FacturacionView'
import LoginView from './components/LoginView'
import DashboardView from './components/DashboardView'
import AdminOverviewView from './components/AdminOverviewView'
import PeriodSelector from './components/PeriodSelector'
import PropuestaView from './components/PropuestaView'
import ComprasView from './components/ComprasView'
import VentasView from './components/VentasView'
import ProcesamientoView from './components/ProcesamientoView'
import ExportacionView from './components/ExportacionView'
import ClientesView from './components/ClientesView'

const STEPS = [
  { id: 1, title: 'Sincronización SIRE', icon: Database, phaseFilter: 'descargados' },
  { id: 2, title: 'Procesamiento IA', icon: BarChart3, phaseFilter: 'enriquecimiento2' },
  { id: 3, title: 'Cierre y Exportación', icon: CheckCircle, phaseFilter: 'preliminar' }
]

const generatePeriods = () => {
  const periods = []
  for (let year = 2025; year <= 2026; year++) {
    for (let month = 1; month <= 12; month++) {
      const mm = month < 10 ? `0${month}` : `${month}`
      periods.push(`${year}${mm}`)
    }
  }
  return periods.reverse()
}
const STATIC_PERIODS = generatePeriods()

const formatPeriod = (periodStr) => {
  if (!periodStr || periodStr.length !== 6) return periodStr;
  const year = periodStr.substring(0, 4);
  const monthNum = parseInt(periodStr.substring(4, 6), 10);
  const months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
  return `${months[monthNum - 1]} ${year}`;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://quanta-production-07d7.up.railway.app'

function App() {
  const [clientes, setClientes] = useState([])
  const [selectedCliente, setSelectedCliente] = useState(() => {
    try { return localStorage.getItem('quanta_selectedCliente') || '' } catch { return '' }
  })
  const [selectedPeriodo, setSelectedPeriodo] = useState(() => {
    try { return localStorage.getItem('quanta_selectedPeriodo') || '' } catch { return '' }
  })
  const [activeStep, setActiveStep] = useState(1)
  const [activeMainTab, setActiveMainTab] = useState(() => {
    try { return localStorage.getItem('quanta_activeMainTab') || 'dashboard' } catch { return 'dashboard' }
  })
  
  const [session, setSession] = useState(null)
  const [userRole, setUserRole] = useState(null)
  const [userClienteId, setUserClienteId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState([])
  const [notifications, setNotifications] = useState([])
  const [clientSearchText, setClientSearchText] = useState('')
  const [showAddClientModal, setShowAddClientModal] = useState(false)
  const [showSettingsModal, setShowSettingsModal] = useState(false)
  const [editingClient, setEditingClient] = useState(null)
  const [newClient, setNewClient] = useState({ ruc: '', razon_social: '', usuario_sol: '', clave_sol: '', rubro: '', cuentas_contables: '' })

  // Terminal state
  const [activeTaskId, setActiveTaskId] = useState('')
  const [terminalLogs, setTerminalLogs] = useState('')
  const [isTerminalMinimized, setIsTerminalMinimized] = useState(false)
  const terminalRef = useRef(null)

  // Simple Pagination
  const [itemsToShow, setItemsToShow] = useState(50)

  const addToast = (msg, type = 'info') => {
    const id = Date.now()
    setNotifications(prev => [...prev, { id, msg, type }])
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id))
    }, 5000)
  }

  const fetchUserRole = async (session) => {
    if (!session) {
      setUserRole(null)
      setUserClienteId(null)
      return
    }
    try {
      const res = await fetch(`${API_BASE_URL}/api/users/me`, {
        headers: { Authorization: `Bearer ${session.access_token}` }
      })
      if (res.ok) {
        const profile = await res.json()
        setUserRole(profile.role || 'client')
        setUserClienteId(profile.cliente_id || null)
        if (profile.role === 'client' && profile.cliente_id) {
          setSelectedCliente(profile.cliente_id)
        }
      } else {
        setUserRole('client')
      }
    } catch (e) {
      console.error("Error fetching user role:", e)
      setUserRole('client')
    }
  }

  useEffect(() => {
    async function loadContext() {
      // Check active session
      const { data: { session } } = await supabase.auth.getSession()
      setSession(session)

      if (session) {
        fetchUserRole(session)
        const { data: clientsData, error } = await supabase.from('clientes').select('*')
        if (error) {
          console.error("Error fetching clientes:", error)
          addToast("Error al cargar clientes: " + error.message, "danger")
        } else if (clientsData) {
          console.log("Clientes loaded:", clientsData.length)
          setClientes(clientsData)
          if (clientsData.length === 0) {
            addToast("0 clientes cargados. Verifica las políticas RLS en Supabase.", "warning")
          }
        }
      }
    }

    loadContext()

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
      if (session) {
        fetchUserRole(session)
        // Reload clients if session changes (e.g. login)
        supabase.from('clientes').select('*').then(({ data }) => {
          if (data) setClientes(data)
        })
      } else {
        setUserRole(null)
      }
    })

    return () => subscription.unsubscribe()
  }, [])

  useEffect(() => {
    if (selectedCliente) {
      const client = clientes.find(c => c.id === selectedCliente)
      setEditingClient(client ? { ...client } : null)
      if (client) setClientSearchText(`${client.ruc} - ${client.razon_social}`)
    } else {
      setEditingClient(null)
      setClientSearchText('')
    }
  }, [selectedCliente, clientes])

  // Recordar la pestaña, cliente y periodo activos para que sobrevivan a un reload.
  useEffect(() => {
    try { localStorage.setItem('quanta_selectedCliente', selectedCliente || '') } catch {}
  }, [selectedCliente])

  useEffect(() => {
    try { localStorage.setItem('quanta_selectedPeriodo', selectedPeriodo || '') } catch {}
  }, [selectedPeriodo])

  useEffect(() => {
    try { localStorage.setItem('quanta_activeMainTab', activeMainTab || '') } catch {}
  }, [activeMainTab])

  // Si la pestaña recordada ya no está permitida para este rol (ej. cambio de usuario
  // en el mismo navegador), no dejar la pantalla en blanco — volver al dashboard.
  useEffect(() => {
    if (!userRole) return
    if (activeMainTab === 'clientes' && !(userRole === 'admin' || userRole === 'accountant')) {
      setActiveMainTab('dashboard')
    } else if (activeMainTab === 'procesamiento' && userRole === 'client') {
      setActiveMainTab('dashboard')
    }
  }, [userRole, activeMainTab])

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [terminalLogs])

  const fetchTableData = async () => {
    if (!selectedCliente || !selectedPeriodo) return;
    setLoading(true)
    setItemsToShow(50)
    try {
      const c_id = selectedCliente;
      const stepConfig = STEPS.find(s => s.id === activeStep)
      const selectedPhase = stepConfig.phaseFilter

      const fetchAllRecords = async (table, selectQuery = '*', filters = {}) => {
        let allData = [];
        let page = 0;
        const pageSize = 1000;
        let fetchMore = true;

        while (fetchMore) {
          let query = supabase.from(table).select(selectQuery).range(page * pageSize, (page + 1) * pageSize - 1);
          Object.keys(filters).forEach(key => {
            query = query.eq(key, filters[key]);
          });
          const { data, error } = await query;
          if (error) {
            console.error('Error fetching data:', error);
            break;
          }
          if (data && data.length > 0) {
            allData = [...allData, ...data];
            page++;
          }
          if (!data || data.length < pageSize) {
            fetchMore = false;
          }
        }
        return allData;
      };

      if (selectedPhase === 'preliminar' || selectedPhase === 'enriquecimiento2') {
        const ventas = await fetchAllRecords('sire_preliminar_ventas', '*', { cliente_id: c_id, periodo: selectedPeriodo });
        const compras = await fetchAllRecords('sire_preliminar_compras', '*', { cliente_id: c_id, periodo: selectedPeriodo });

        const allE = [...(ventas || []).map(v => ({...v, tipo: 'VENTA'})), ...(compras || []).map(c => ({...c, tipo: 'COMPRA'}))]

        if (selectedPhase === 'preliminar') {
          setData(allE)
        } else if (selectedPhase === 'enriquecimiento2') {
          setData(allE.filter(x => x.estado_enriquecimiento === 'COMPLETO'))
        }
        
      } else if (selectedPhase === 'descargados') {
        const fisicos = await fetchAllRecords('sire_comprobantes_fisicos', '*, sire_preliminar_compras(fecha_emision, total_cp), sire_preliminar_ventas(fecha_emision, total_cp)', { cliente_id: selectedCliente, periodo: selectedPeriodo });
          
        let localFiles = []
        try {
          const res = await fetch(`${API_BASE_URL}/api/bot/local-files`)
          if (res.ok) {
            const json = await res.json()
            localFiles = json.files || []
          }
        } catch(e) {}
        
        const enrichedFisicos = (fisicos || []).map(f => {
          const rucTercero = f.ruc_tercero || ''
          const tipoCp = f.tipo_cp || ''
          const baseName = `${rucTercero}-${tipoCp}-${f.serie || ''}-${f.numero || ''}`
          
          if (localFiles.includes(`${baseName}.xml`) || localFiles.includes(`${baseName}.zip`)) f.estado_xml = 'DESCARGADO'
          if (localFiles.includes(`${baseName}.pdf`)) f.estado_pdf = 'DESCARGADO'

          if (f.sire_preliminar_compras) {
            f.fecha_emision = f.sire_preliminar_compras.fecha_emision;
            f.total_cp = f.sire_preliminar_compras.total_cp;
          } else if (f.sire_preliminar_ventas) {
            f.fecha_emision = f.sire_preliminar_ventas.fecha_emision;
            f.total_cp = f.sire_preliminar_ventas.total_cp;
          }
          
          return f
        })
        setData(enrichedFisicos)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTableData()
  }, [selectedCliente, selectedPeriodo, activeStep])

  useEffect(() => {
    let interval = null;
    if (activeTaskId) {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`${API_BASE_URL}/api/bot/logs/${activeTaskId}`)
          if (res.ok) {
            const data = await res.json()
            setTerminalLogs(data.logs)
            if (data.is_running === false && data.logs !== "No logs available yet...") {
              fetchTableData(); // Refresh immediately
              setTimeout(() => {
                setActiveTaskId('')
                setIsTerminalMinimized(true)
              }, 2000)
            }
          }
        } catch(e) {
          console.error("Error fetching logs", e)
        }
      }, 1000)
    }
    return () => { if (interval) clearInterval(interval) }
  }, [activeTaskId, selectedCliente, selectedPeriodo, activeStep])

  useEffect(() => {
    let intervalId
    if (activeTaskId) {
      intervalId = setInterval(() => { fetchTableData() }, 5000)
    }
    return () => { if (intervalId) clearInterval(intervalId) }
  }, [activeTaskId, selectedCliente, selectedPeriodo, activeStep])

  const waitForTask = (taskId) => {
    return new Promise((resolve) => {
      const interval = setInterval(async () => {
        try {
          const res = await fetch(`${API_BASE_URL}/api/bot/logs/${taskId}`)
          if (res.ok) {
            const data = await res.json()
            if (data.is_running === false) {
              clearInterval(interval)
              resolve(true)
            }
          }
        } catch(e) {
          clearInterval(interval)
          resolve(false)
        }
      }, 2000)
    })
  }

  const handleBotActionRaw = async (action, extraPayload = {}) => {
    const cliente = clientes.find(c => c.id === selectedCliente)
    if (!cliente) return {ok: false}
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/bot/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ruc: cliente.ruc, periodo: selectedPeriodo, ...extraPayload })
      })
      const result = await response.json()
      return {ok: response.ok, ...result}
    } catch (e) {
      return {ok: false, detail: 'Error de conexión'}
    }
  }

  const handleBotAction = async (action, extraPayload = {}) => {
    addToast(`Enviando orden de ejecución...`, 'info')
    setTerminalLogs('Iniciando tarea...\n')
    setIsTerminalMinimized(false)
    
    const result = await handleBotActionRaw(action, extraPayload)
    if (result.ok) {
      addToast(`✅ ${result.message}`, 'success')
      if (result.task_id) setActiveTaskId(result.task_id)
    } else {
      addToast(`❌ Error: ${result.detail || 'Error en el servidor'}`, 'danger')
      setTerminalLogs(`Error de API: ${result.detail || 'Desconocido'}\n`)
    }
  }

  const handleSyncSireFisicos = async () => {
    const cliente = clientes.find(c => c.id === selectedCliente)
    if (!cliente || !selectedPeriodo) return

    const hasCreds = cliente.client_id_api && cliente.client_secret_api
    
    if (!hasCreds) {
      addToast('Verificando credenciales mediante automatización...', 'info')
      setTerminalLogs('Generando credenciales API...\n')
      const loginRes = await handleBotActionRaw('automation-login')
      if (loginRes.ok) {
        if (loginRes.task_id) {
          setActiveTaskId(loginRes.task_id)
          await waitForTask(loginRes.task_id)
        }
      } else {
        addToast('❌ Error al generar credenciales', 'danger')
        return
      }
    }
    
    addToast('Iniciando descarga de comprobantes físicos...', 'info')
    handleBotAction('download-fisicos')
  }
  const handleResetPendientes = async () => {
    const cliente = clientes.find(c => c.id === selectedCliente)
    if (!cliente || !selectedPeriodo) return

    if (!window.confirm("¿Seguro que quieres pasar todos los comprobantes fallidos a PENDIENTE para que el bot los reintente?")) return;

    addToast('Reiniciando estado de comprobantes...', 'info')
    try {
      const response = await fetch(`${API_BASE_URL}/api/comprobantes/reset-pendientes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ruc: cliente.ruc, periodo: selectedPeriodo })
      })
      const result = await response.json()
      if (response.ok) {
        addToast(`✅ ${result.mensaje}`, 'success')
        fetchData() // Refresh table
      } else {
        addToast(`❌ Error: ${result.detail || 'Error en servidor'}`, 'danger')
      }
    } catch (e) {
      addToast(`Error de conexión`, 'danger')
    }
  }

  const handleManualUpload = async (comprobanteId, file, fileType) => {
    if (!file) return;
    const formData = new FormData()
    formData.append('file', file)
    formData.append('file_type', fileType)

    addToast(`Subiendo ${fileType.toUpperCase()}...`, 'info')
    try {
      const response = await fetch(`${API_BASE_URL}/api/comprobante/${comprobanteId}/upload`, {
        method: 'POST',
        body: formData
      })
      const result = await response.json()
      if (response.ok) {
        addToast(`✅ ${fileType.toUpperCase()} subido correctamente`, 'success')
        fetchData() // Refresh table
      } else {
        addToast(`❌ Error: ${result.detail || 'Error al subir archivo'}`, 'danger')
      }
    } catch (e) {
      addToast(`Error de conexión al subir archivo`, 'danger')
    }
  }

  const handleAddClient = async () => {
    if (!newClient.ruc || !newClient.razon_social) {
      addToast('RUC y Razón Social son obligatorios', 'warning')
      return
    }
    const { data, error } = await supabase.from('clientes').insert([newClient]).select()
    if (error) {
      addToast(`Error al agregar: ${error.message}`, 'danger')
    } else if (data && data.length > 0) {
      addToast('Cliente agregado correctamente', 'success')
      setClientes([...clientes, data[0]])
      setSelectedCliente(data[0].id)
      setShowAddClientModal(false)
      setNewClient({ ruc: '', razon_social: '', usuario_sol: '', clave_sol: '', rubro: '', cuentas_contables: '' })
    }
  }

  const handleSaveClient = async () => {
    if (!editingClient) return
    const { error } = await supabase.from('clientes').update({
      usuario_sol: editingClient.usuario_sol,
      clave_sol: editingClient.clave_sol,
      client_id_api: editingClient.client_id_api,
      client_secret_api: editingClient.client_secret_api,
      rubro: editingClient.rubro,
      cuentas_contables: editingClient.cuentas_contables
    }).eq('id', editingClient.id)

    if (error) addToast(`Error al guardar: ${error.message}`, 'danger')
    else {
      addToast('Credenciales guardadas', 'success')
      setClientes(clientes.map(c => c.id === editingClient.id ? editingClient : c))
      setShowSettingsModal(false)
    }
  }

  const handleExportExcel = (urlOrAction) => {
    if (!selectedCliente || !selectedPeriodo) return
    const url = `${API_BASE_URL}/api/export/excel/${selectedCliente}/${selectedPeriodo}`
    const a = document.createElement('a')
    a.href = url
    a.download = true
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }

  const handleExportPdfs = async (tipo_libro) => {
    const cliente = clientes.find(c => c.id === selectedCliente)
    if (!cliente) return
    
    addToast(`Generando PDF consolidado de ${tipo_libro}...`, 'info')
    try {
      const response = await fetch(`${API_BASE_URL}/api/export/pdf-merged`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ruc: cliente.ruc, periodo: selectedPeriodo, tipo_libro, allow_incomplete: true })
      })
      if (!response.ok) {
        const errorData = await response.json()
        addToast(`Error: ${errorData.detail || 'Error al generar PDF'}`, 'danger')
        return
      }
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Comprobantes_${tipo_libro}_${selectedPeriodo}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      addToast(`PDF consolidado de ${tipo_libro} descargado.`, 'success')
    } catch (e) {
      addToast(`Error de conexión al exportar.`, 'danger')
    }
  }

  const handleExportPreliminarExcel = async () => {
    const cliente = clientes.find(c => c.id === selectedCliente)
    if (!cliente || !selectedPeriodo) return
    
    addToast(`Generando Excel Preliminar con liquidación de impuestos...`, 'info')
    try {
      const response = await fetch(`${API_BASE_URL}/api/export/preliminar-excel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ruc: cliente.ruc, periodo: selectedPeriodo })
      })
      if (!response.ok) {
        addToast(`Error al generar Excel preliminar`, 'danger')
        return
      }
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Preliminar_${cliente.ruc}_${selectedPeriodo}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      addToast(`Excel Preliminar descargado.`, 'success')
    } catch (e) {
      addToast(`Error de conexión al exportar.`, 'danger')
    }
  }

  const currentClient = clientes.find(c => c.id === selectedCliente)
  const isReadyToProcess = selectedCliente && selectedPeriodo

  const handleLogout = async () => {
    await supabase.auth.signOut()
    setSession(null)
  }

  if (!session) {
    return <LoginView onLoginSuccess={(sess) => setSession(sess)} />
  }

  return (
    <div className="app-layout">
      <div className="app-container">
        {/* Sidebar */}
        <aside className="sidebar animate-slide-up">
          <div className="brand">
            <div className="brand-icon">Q</div>
            <h1>Quanta</h1>
          </div>

          {/* Main tab navigation */}
          <div className="menu-label">Menu</div>
          <div className="main-tabs-container">
            <button
              className={`main-tab-btn ${activeMainTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveMainTab('dashboard')}
            >
              <BarChart2 size={18} />
              <span>Dashboard</span>
            </button>
            {userRole === 'admin' && (
              <button
                className={`main-tab-btn ${activeMainTab === 'resumen-general' ? 'active' : ''}`}
                onClick={() => setActiveMainTab('resumen-general')}
              >
                <Building2 size={18} />
                <span>Resumen General</span>
              </button>
            )}
            <button 
              className={`main-tab-btn ${activeMainTab === 'propuesta' ? 'active' : ''}`}
              onClick={() => setActiveMainTab('propuesta')}
            >
              <FileText size={18} />
              <span>Propuesta</span>
            </button>
            <button 
              className={`main-tab-btn ${activeMainTab === 'compras' ? 'active' : ''}`}
              onClick={() => setActiveMainTab('compras')}
            >
              <Upload size={18} />
              <span>Compras</span>
            </button>
            <button 
              className={`main-tab-btn ${activeMainTab === 'ventas' ? 'active' : ''}`}
              onClick={() => setActiveMainTab('ventas')}
            >
              <Database size={18} />
              <span>Ventas</span>
            </button>
            {userRole !== 'client' && (
              <button
                className={`main-tab-btn ${activeMainTab === 'procesamiento' ? 'active' : ''}`}
                onClick={() => setActiveMainTab('procesamiento')}
              >
                <Activity size={18} />
                <span>Procesamiento</span>
              </button>
            )}
            <button 
              className={`main-tab-btn ${activeMainTab === 'exportacion' ? 'active' : ''}`}
              onClick={() => setActiveMainTab('exportacion')}
            >
              <Download size={18} />
              <span>Exportación</span>
            </button>
            {(userRole === 'admin' || userRole === 'accountant') && (
              <button
                className={`main-tab-btn ${activeMainTab === 'clientes' ? 'active' : ''}`}
                onClick={() => setActiveMainTab('clientes')}
              >
                <Users size={18} />
                <span>Clientes</span>
              </button>
            )}
          </div>

          <div className="sidebar-controls">
            <div className="menu-label">Sistema</div>
            <button
              className="main-tab-btn"
              onClick={handleLogout}
            >
              <LogOut size={18} />
              <span>Cerrar Sesión</span>
            </button>
          </div>
      </aside>

      <div className="main-area">
        {/* Top Bar */}
        <header className="top-bar">
          <div className="top-bar-controls" style={{display: 'flex', gap: '2rem', alignItems: 'center', justifyContent: 'center', flex: 1}}>
            {userRole === 'client' ? (
              <div className="control-group" style={{flex: '0 1 350px'}}>
                <div style={{display: 'flex', gap: '0.75rem', alignItems: 'center'}}>
                  <span style={{fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em'}}>Empresa</span>
                  <div style={{flex: 1, padding: '0.65rem 1.2rem', borderRadius: '24px', border: '1px solid rgba(255,255,255,0.08)', background: 'rgba(255,255,255,0.02)', color: 'var(--text-main)', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                    <Building2 size={15} color="var(--text-muted)" />
                    {currentClient ? currentClient.ruc : 'Cargando...'}
                  </div>
                </div>
              </div>
            ) : (
              <div className="control-group" style={{flex: '0 1 350px'}}>
                <div style={{display: 'flex', gap: '0.75rem', alignItems: 'center'}}>
                  <span style={{fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em'}}>Cliente</span>
                  <input
                    list="clientes-datalist"
                    placeholder="Buscar RUC o Nombre..."
                    value={clientSearchText}
                    onChange={e => {
                      const val = e.target.value;
                      setClientSearchText(val);
                      const found = clientes.find(c => `${c.ruc} - ${c.razon_social}` === val);
                      if (found) setSelectedCliente(found.id);
                      else if (val === '') setSelectedCliente('');
                    }}
                    style={{flex: 1, padding: '0.65rem 1.2rem', borderRadius: '24px', border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(255,255,255,0.05)', color: 'var(--text-main)', fontSize: '0.9rem', outline: 'none'}}
                  />
                </div>
                <datalist id="clientes-datalist">
                  {clientes.map(c => <option key={c.id} value={`${c.ruc} - ${c.razon_social}`} />)}
                </datalist>
              </div>
            )}

            <div className="control-group" style={{flex: '0 1 220px'}}>
              <div style={{display: 'flex', gap: '0.75rem', alignItems: 'center'}}>
                <span style={{fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em'}}>Periodo</span>
                <PeriodSelector 
                  value={selectedPeriodo} 
                  onChange={setSelectedPeriodo}
                />
              </div>
            </div>
          </div>
          
          <div className="top-icons">
            <div className="user-profile">
              <img src="https://i.pravatar.cc/100?img=11" alt="Profile" />
              <div className="user-info">
                <span className="user-name">Administrador</span>
                <span className="user-email">{session?.user?.email}</span>
              </div>
            </div>
          </div>
        </header>

        {/* TABS PRINCIPALES */}
        <main className="main-content animate-fade-in" style={{animationDelay: '0.1s'}}>
          {activeMainTab === 'propuesta' ? (
            <PropuestaView currentClient={currentClient} selectedPeriodo={selectedPeriodo} userRole={userRole} />
          ) : activeMainTab === 'compras' ? (
            <ComprasView currentClient={currentClient} selectedPeriodo={selectedPeriodo} userRole={userRole} />
          ) : activeMainTab === 'ventas' ? (
            <VentasView currentClient={currentClient} selectedPeriodo={selectedPeriodo} userRole={userRole} />
          ) : activeMainTab === 'procesamiento' && userRole !== 'client' ? (
            <ProcesamientoView currentClient={currentClient} selectedPeriodo={selectedPeriodo} userRole={userRole} />
          ) : activeMainTab === 'exportacion' ? (
            <ExportacionView currentClient={currentClient} selectedPeriodo={selectedPeriodo} />
          ) : activeMainTab === 'clientes' && (userRole === 'admin' || userRole === 'accountant') ? (
            <ClientesView setActiveMainTab={setActiveMainTab} />
          ) : activeMainTab === 'resumen-general' && userRole === 'admin' ? (
            <AdminOverviewView selectedPeriodo={selectedPeriodo} />
          ) : activeMainTab === 'dashboard' ? (
            <DashboardView currentClient={currentClient} selectedPeriodo={selectedPeriodo} userRole={userRole} />
          ) : (
            <div className="dashboard-placeholder" style={{flex: 1, backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: '16px', border: '1px dashed rgba(255,255,255,0.15)', minHeight: '400px'}}></div>
          )}
        </main>
      </div> {/* End main-area */}
      
      {/* Settings Modal */}
      {showSettingsModal && editingClient && (
        <div className="modal-overlay" onClick={() => setShowSettingsModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div style={{display:'flex', justifyContent:'space-between', marginBottom:'1.5rem'}}>
              <h3 style={{color:'#f8fafc'}}>Configuración de Cliente</h3>
              <button onClick={() => setShowSettingsModal(false)} style={{background:'none', border:'none', color:'#94a3b8', cursor:'pointer'}}><X size={20}/></button>
            </div>
            
            <div className="control-group" style={{marginBottom: '1rem'}}>
              <label>RUC</label>
              <input type="text" value={editingClient.ruc} disabled />
            </div>
            <div className="control-group" style={{marginBottom: '1rem'}}>
              <label>Razón Social</label>
              <input type="text" value={editingClient.razon_social} disabled />
            </div>
            <div style={{display:'flex', gap:'1rem', marginBottom: '1rem'}}>
              <div className="control-group" style={{flex: 1}}>
                <label>Usuario SOL</label>
                <input type="text" value={editingClient.usuario_sol || ''} onChange={e => setEditingClient({...editingClient, usuario_sol: e.target.value})} />
              </div>
              <div className="control-group" style={{flex: 1}}>
                <label>Clave SOL</label>
                <input type="text" value={editingClient.clave_sol || ''} onChange={e => setEditingClient({...editingClient, clave_sol: e.target.value})} />
              </div>
            </div>
            <div style={{display:'flex', gap:'1rem', marginBottom: '1rem'}}>
              <div className="control-group" style={{flex: 1}}>
                <label>Client ID (API)</label>
                <input type="text" value={editingClient.client_id_api || ''} onChange={e => setEditingClient({...editingClient, client_id_api: e.target.value})} />
              </div>
              <div className="control-group" style={{flex: 1}}>
                <label>Client Secret (API)</label>
                <input type="text" value={editingClient.client_secret_api || ''} onChange={e => setEditingClient({...editingClient, client_secret_api: e.target.value})} />
              </div>
            </div>
            
            <div className="control-group" style={{marginBottom: '1rem'}}>
              <label>Cuentas Contables (Personalizadas)</label>
              <textarea 
                placeholder="Ej: 6011 (Mercaderías), 6311 (Transporte)"
                value={editingClient.cuentas_contables || ''} 
                onChange={e => setEditingClient({...editingClient, cuentas_contables: e.target.value})} 
                rows="3"
                style={{
                  fontFamily: 'Inter', background: 'rgba(0, 0, 0, 0.3)', 
                  border: '1px solid rgba(255, 255, 255, 0.1)', color: 'var(--text-main)', 
                  padding: '0.6rem 1rem', borderRadius: '8px', width: '100%', resize: 'vertical'
                }}
              />
              <span style={{fontSize: '0.75rem', color: 'var(--text-muted)'}}>
                La Inteligencia Artificial usará SOLAMENTE estas cuentas para este cliente. Si está vacío, usará el Plan Contable general.
              </span>
            </div>
            
            <div style={{display:'flex', justifyContent:'flex-end', gap:'1rem', marginTop:'2rem'}}>
              <button className="btn btn-secondary" style={{width:'auto'}} onClick={() => setShowSettingsModal(false)}>Cancelar</button>
              <button className="btn btn-primary" style={{width:'auto'}} onClick={handleSaveClient}>Guardar Cambios</button>
            </div>
          </div>
        </div>
      )}

      {/* Add Client Modal */}
      {showAddClientModal && (
        <div className="modal-overlay" onClick={() => setShowAddClientModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div style={{display:'flex', justifyContent:'space-between', marginBottom:'1.5rem'}}>
              <h3 style={{color:'#f8fafc'}}>Agregar Nuevo Cliente</h3>
              <button onClick={() => setShowAddClientModal(false)} style={{background:'none', border:'none', color:'#94a3b8', cursor:'pointer'}}><X size={20}/></button>
            </div>
            <div className="control-group" style={{marginBottom: '1rem'}}>
              <label>RUC *</label>
              <input type="text" value={newClient.ruc} onChange={e => setNewClient({...newClient, ruc: e.target.value})} placeholder="Ej: 20123456789" />
            </div>
            <div className="control-group" style={{marginBottom: '1rem'}}>
              <label>Razón Social *</label>
              <input type="text" value={newClient.razon_social} onChange={e => setNewClient({...newClient, razon_social: e.target.value})} placeholder="Ej: MI EMPRESA S.A.C." />
            </div>
            <div className="control-group" style={{marginBottom: '1rem'}}>
              <label>Rubro / Giro de Negocio</label>
              <input type="text" value={newClient.rubro || ''} onChange={e => setNewClient({...newClient, rubro: e.target.value})} placeholder="Ej: Venta de abarrotes, Transporte..." />
            </div>
            <div className="control-group" style={{marginBottom: '1rem'}}>
              <label>Cuentas Contables (Personalizadas)</label>
              <textarea 
                placeholder="Ej: 6011 (Mercaderías), 6311 (Transporte)"
                value={newClient.cuentas_contables || ''} 
                onChange={e => setNewClient({...newClient, cuentas_contables: e.target.value})} 
                rows="2"
                style={{
                  fontFamily: 'Inter', background: 'rgba(0, 0, 0, 0.3)', 
                  border: '1px solid rgba(255, 255, 255, 0.1)', color: 'var(--text-main)', 
                  padding: '0.6rem 1rem', borderRadius: '8px', width: '100%', resize: 'vertical'
                }}
              />
            </div>
            <div style={{display:'flex', justifyContent:'flex-end', gap:'1rem', marginTop:'2rem'}}>
              <button className="btn btn-secondary" style={{width:'auto'}} onClick={() => setShowAddClientModal(false)}>Cancelar</button>
              <button className="btn btn-primary" style={{width:'auto'}} onClick={handleAddClient}>Guardar Cliente</button>
            </div>
          </div>
        </div>
      )}

      {/* Toasts */}
      <div className="toast-container">
        {notifications.map(n => (
          <div key={n.id} className="toast" style={{
            borderLeft: `4px solid ${n.type === 'success' ? 'var(--success)' : n.type === 'danger' ? 'var(--danger)' : n.type === 'warning' ? 'var(--warning)' : 'var(--accent-primary)'}`
          }}>
            {n.msg}
          </div>
        ))}
      </div>
      </div> {/* End app-container */}
    </div>
  )
}

export default App
