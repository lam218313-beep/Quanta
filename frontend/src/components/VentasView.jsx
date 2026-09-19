import React, { useState, useEffect, useRef, useCallback } from 'react';
import { DownloadCloud, Database, Search, DollarSign, FileText, Activity, CheckCircle, FileCode, FileIcon, Check, X, Loader2, Terminal, ChevronDown, ChevronUp } from 'lucide-react';
import { supabase } from '../supabaseClient';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://quanta-production-07d7.up.railway.app';

export default function VentasView({ currentClient, selectedPeriodo, userRole }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const [taskRunning, setTaskRunning] = useState(false);
  const [taskStage, setTaskStage] = useState('');
  const [taskLog, setTaskLog] = useState('');
  const [showLog, setShowLog] = useState(false);
  const intervalRef = useRef(null);
  const logBoxRef = useRef(null);

  const fetchData = useCallback(async () => {
    if (!currentClient || !selectedPeriodo) {
      setData([]);
      return;
    }
    setLoading(true);

    const [ventasRes, fisicosRes] = await Promise.all([
      supabase.from('sire_preliminar_ventas').select('*').eq('cliente_id', currentClient.id).eq('periodo', selectedPeriodo),
      supabase.from('sire_comprobantes_fisicos').select('*').eq('cliente_id', currentClient.id).eq('periodo', selectedPeriodo).eq('tipo_libro', 'VENTAS')
    ]);

    if (ventasRes.error) console.error('Error fetching ventas:', ventasRes.error);
    if (fisicosRes.error) console.error('Error fetching fisicos:', fisicosRes.error);

    const ventas = ventasRes.data || [];
    const fisicos = fisicosRes.data || [];

    const combined = ventas.map(c => {
      const fisico = fisicos.find(f => f.preliminar_venta_id === c.id);
      return {
        ...c,
        estado_xml: fisico?.estado_xml || 'NO_INICIADO',
        estado_pdf: fisico?.estado_pdf || 'NO_INICIADO',
        ruta_xml: fisico?.ruta_xml,
        ruta_pdf: fisico?.ruta_pdf,
      };
    });

    setData(combined);
    setLoading(false);
  }, [currentClient, selectedPeriodo]);

  useEffect(() => { fetchData(); }, [fetchData]);

  useEffect(() => () => { if (intervalRef.current) clearInterval(intervalRef.current); }, []);

  useEffect(() => {
    if (taskLog && logBoxRef.current) logBoxRef.current.scrollTop = logBoxRef.current.scrollHeight;
  }, [taskLog]);

  const runTaskToCompletion = (taskId) => new Promise((resolve) => {
    intervalRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/bot/logs/${taskId}`);
        const body = await res.json();
        setTaskLog(body.logs || '');
        if (!body.is_running) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
          resolve();
        }
      } catch (e) {
        console.error('Error polling task logs:', e);
      }
    }, 2500);
  });

  const startTask = async (endpoint, payload) => {
    const res = await fetch(`${API_BASE_URL}/api/bot/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const body = await res.json();
    if (!res.ok) throw new Error(body.detail || 'No se pudo iniciar la tarea.');
    return body.task_id;
  };

  const handleAutenticarDescargar = async () => {
    if (!currentClient || !selectedPeriodo) {
      alert('Selecciona un cliente y un periodo primero.');
      return;
    }
    setTaskRunning(true);
    setTaskLog('');
    setShowLog(true);
    try {
      setTaskStage('Autenticando en SUNAT...');
      const loginTaskId = await startTask('automation-login', { ruc: currentClient.ruc });
      await runTaskToCompletion(loginTaskId);

      setTaskStage('Descargando comprobantes físicos...');
      const dlTaskId = await startTask('download-fisicos', { ruc: currentClient.ruc, periodo: selectedPeriodo, tipo_libro: 'VENTAS' });
      await runTaskToCompletion(dlTaskId);

      fetchData();
    } catch (err) {
      console.error(err);
      alert(err.message || 'Error al autenticar/descargar físicos.');
    } finally {
      setTaskRunning(false);
      setTaskStage('');
    }
  };

  const filteredData = data.filter(r => 
    (r.razon_social?.toLowerCase() || '').includes(searchTerm.toLowerCase()) || 
    (r.nro_doc_identidad || '').includes(searchTerm) ||
    (r.nro_cp || '').includes(searchTerm)
  );

  // El backend (sire_bot_orchestrator.py / sync_files.py) escribe estos estados reales:
  // 'DESCARGADO' (ok), 'PENDIENTE'/'ERROR' (aun no), 'NO_DESCARGABLE'/'NO_EXISTE' (SUNAT no lo ofrece).
  // 'COMPLETADO' nunca se escribe — usarlo aqui hacia que las tarjetas/iconos nunca reflejaran una descarga real.
  const isDownloaded = (status) => status === 'DESCARGADO' || status === 'COMPLETADO';
  const isUnavailable = (status) => status === 'NO_DESCARGABLE' || status === 'NO_EXISTE';

  const totalSoles = data.reduce((acc, curr) => acc + Number(curr.total_cp || 0), 0);
  const comprobantesCount = data.length;
  const processedCount = data.filter(r => isDownloaded(r.estado_xml) || isDownloaded(r.estado_pdf)).length;
  const pendientesCount = comprobantesCount - processedCount;

  const getStatusIcon = (status) => {
    if (isDownloaded(status)) return <Check size={16} color="#10b981" />;
    if (status === 'PENDIENTE' || status === 'ERROR') return <Activity size={16} color="#f59e0b" />;
    if (isUnavailable(status)) return <X size={16} color="#94a3b8" />;
    return <span style={{fontSize: '0.7rem', color: '#94a3b8'}}>-</span>;
  };

  return (
    <div className="view-container animate-fade-in" style={{padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%'}}>
      {/* Top Actions */}
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <div>
          <h2 style={{fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-main)', margin: 0}}>Ventas</h2>
          <p style={{color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.25rem'}}>Gestión de comprobantes físicos y electrónicos de ventas.</p>
        </div>
        {userRole !== 'client' && (
          <div style={{display: 'flex', gap: '0.75rem', alignItems: 'center'}}>
            {taskLog && (
              <button className="btn btn-outline" style={{padding: '0.6rem 0.8rem'}} onClick={() => setShowLog(!showLog)} title="Ver registro">
                <Terminal size={16} /> {showLog ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>
            )}
            <button className="btn btn-primary" style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}} onClick={handleAutenticarDescargar} disabled={taskRunning}>
              {taskRunning ? <Loader2 size={16} className="spin" /> : <DownloadCloud size={16} />}
              {taskRunning ? (taskStage || 'Procesando...') : 'Autenticar y Descargar Físicos'}
            </button>
          </div>
        )}
      </div>

      {showLog && (
        <div className="glass-panel" style={{padding: '1rem', fontFamily: 'monospace', fontSize: '0.78rem'}}>
          <div ref={logBoxRef} style={{maxHeight: '180px', overflowY: 'auto', color: '#94a3b8', whiteSpace: 'pre-wrap', lineHeight: 1.5}}>
            {taskLog || 'Esperando salida del bot...'}
          </div>
        </div>
      )}

      {/* Metrics Cards */}
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem'}}>
        {[
          { title: 'Total Ventas', value: `S/ ${totalSoles.toFixed(2)}`, icon: DollarSign, color: '#2563eb' },
          { title: 'Comprobantes', value: comprobantesCount.toString(), icon: FileText, color: '#8b5cf6' },
          { title: 'Pendientes', value: pendientesCount.toString(), icon: Activity, color: '#f59e0b' },
          { title: 'Procesados', value: processedCount.toString(), icon: CheckCircle, color: '#10b981' },
        ].map((metric, i) => (
          <div key={i} className="glass-panel" style={{padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem'}}>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
              <span style={{color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase'}}>{metric.title}</span>
              <div style={{padding: '0.5rem', background: `${metric.color}15`, borderRadius: '8px', color: metric.color}}>
                <metric.icon size={18} />
              </div>
            </div>
            <div style={{fontSize: '1.8rem', fontWeight: 700, color: 'var(--text-main)'}}>
              {metric.value}
            </div>
          </div>
        ))}
      </div>

      {/* Table Section */}
      <div className="glass-panel data-panel" style={{flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden'}}>
        <div className="table-header-actions" style={{padding: '1rem', borderBottom: '1px solid rgba(226, 232, 240, 0.8)', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <div className="table-title" style={{display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: 'var(--text-main)'}}>
            <Database size={18} color="var(--accent-primary)" />
            Registro de Ventas ({filteredData.length})
          </div>
          
          <div className="search-box" style={{width: '250px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', display: 'flex', alignItems: 'center', padding: '0.4rem 0.8rem'}}>
            <Search size={14} color="var(--text-muted)" style={{marginRight: '0.5rem'}} />
            <input 
              type="text" 
              placeholder="Buscar (RUC, Nombre, Nro)..." 
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              style={{border: 'none', background: 'transparent', outline: 'none', fontSize: '0.85rem', color: 'var(--text-main)', width: '100%'}}
            />
          </div>
        </div>
        
        <div className="table-container" style={{flex: 1, overflow: 'auto', padding: '1rem'}}>
          {loading ? (
            <div style={{textAlign: 'center', padding: '3rem', color: 'var(--text-muted)'}}>Cargando datos...</div>
          ) : !currentClient || !selectedPeriodo ? (
            <div style={{textAlign: 'center', padding: '3rem', color: 'var(--text-muted)'}}>Seleccione un cliente y periodo para ver las ventas.</div>
          ) : filteredData.length === 0 ? (
            <div style={{textAlign: 'center', padding: '3rem', color: 'var(--text-muted)'}}>
              <FileText size={48} style={{opacity: 0.3, margin: '0 auto 1rem auto', display: 'block'}} />
              No se encontraron comprobantes para el periodo seleccionado.
            </div>
          ) : (
            <table style={{width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem'}}>
              <thead>
                <tr style={{textAlign: 'left', borderBottom: '2px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)'}}>
                  <th style={{padding: '0.75rem 0.5rem'}}>F. Emisión</th>
                  <th style={{padding: '0.75rem 0.5rem'}}>RUC / Cliente</th>
                  <th style={{padding: '0.75rem 0.5rem'}}>Comprobante</th>
                  <th style={{padding: '0.75rem 0.5rem', textAlign: 'right'}}>Total</th>
                  <th style={{padding: '0.75rem 0.5rem', textAlign: 'center'}}>XML</th>
                  <th style={{padding: '0.75rem 0.5rem', textAlign: 'center'}}>PDF</th>
                  <th style={{padding: '0.75rem 0.5rem', textAlign: 'right'}}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredData.map((row) => (
                  <tr key={row.id} style={{borderBottom: '1px solid rgba(255,255,255,0.06)'}}>
                    <td style={{padding: '0.75rem 0.5rem'}}>{row.fecha_emision}</td>
                    <td style={{padding: '0.75rem 0.5rem'}}>
                      <div style={{fontWeight: 600, color: 'var(--text-main)'}}>{row.nro_doc_identidad}</div>
                      <div style={{fontSize: '0.75rem', color: 'var(--text-muted)', maxWidth: '200px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}} title={row.razon_social}>
                        {row.razon_social}
                      </div>
                    </td>
                    <td style={{padding: '0.75rem 0.5rem'}}>
                      <span className="badge" style={{background: 'rgba(99,102,241,0.15)', color: '#818cf8'}}>{row.tipo_cp_doc}</span>
                      <span style={{marginLeft: '0.5rem', fontFamily: 'monospace'}}>{row.serie_cdp}-{row.nro_cp}</span>
                    </td>
                    <td style={{padding: '0.75rem 0.5rem', textAlign: 'right', fontFamily: 'monospace', fontWeight: 600}}>
                      {Number(row.total_cp || 0).toFixed(2)}
                    </td>
                    <td style={{padding: '0.75rem 0.5rem', textAlign: 'center'}}>
                      <div style={{display: 'flex', justifyContent: 'center'}} title={row.estado_xml}>
                        {getStatusIcon(row.estado_xml)}
                      </div>
                    </td>
                    <td style={{padding: '0.75rem 0.5rem', textAlign: 'center'}}>
                      <div style={{display: 'flex', justifyContent: 'center'}} title={row.estado_pdf}>
                        {getStatusIcon(row.estado_pdf)}
                      </div>
                    </td>
                    <td style={{padding: '0.75rem 0.5rem', textAlign: 'right'}}>
                      <div style={{display: 'flex', gap: '0.5rem', justifyContent: 'flex-end'}}>
                        <button className="btn btn-outline" style={{padding: '0.3rem', borderColor: 'rgba(255,255,255,0.15)', color: '#94a3b8'}} title="Descargar XML">
                          <FileCode size={14} />
                        </button>
                        <button className="btn btn-outline" style={{padding: '0.3rem', borderColor: 'rgba(239,68,68,0.4)', color: '#f87171'}} title="Descargar PDF">
                          <FileIcon size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
