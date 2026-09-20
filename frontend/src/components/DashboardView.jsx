import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import {
  TrendingUp, TrendingDown, DollarSign, Activity, FileText,
  Loader2, AlertCircle, CheckCircle2, XCircle, Users, Scale, ShoppingBag, Building2, Download
} from 'lucide-react';
import { supabase } from '../supabaseClient';
import AttachmentsDropzone from './AttachmentsDropzone';
import './DashboardView.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://quanta-production-07d7.up.railway.app';

const formatCurrency = (value) => {
  return new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' }).format(value || 0);
};

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

// Catálogo SUNAT 01 (Tipo de Comprobante de Pago) — solo los códigos que
// realmente aparecen en compras/ventas SIRE.
const TIPO_CP_LABELS = {
  '01': 'Factura',
  '03': 'Boleta',
  '07': 'N. Crédito',
  '08': 'N. Débito',
  '09': 'Guía Remisión',
  '20': 'Retención',
  '40': 'Percepción',
};
const getTipoCpLabel = (code) => TIPO_CP_LABELS[code] || (code ? `Tipo ${code}` : 'Sin tipo');

const ESTADO_LABELS = {
  PENDIENTE: 'Pendiente',
  PARCIAL: 'Parcial',
  ERROR: 'Error',
  COMPLETO: 'Completo',
};

export default function DashboardView({ currentClient, selectedPeriodo, userRole }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Data states
  const [documentos, setDocumentos] = useState([]);
  const [pagos, setPagos] = useState([]);
  const [downloadingPdf, setDownloadingPdf] = useState(false);

  useEffect(() => {
    if (currentClient && selectedPeriodo) {
      loadDashboardData();
    }
  }, [currentClient, selectedPeriodo]);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch Libro Unificado for the current client and period
      const { data: docData, error: docError } = await supabase
        .from('v_libro_unificado')
        .select('*')
        .eq('ruc', currentClient.ruc)
        .eq('periodo', selectedPeriodo)
        .order('fecha_emision', { ascending: false });

      if (docError) throw docError;

      // 2. Fetch CRM Payments to show billing status (optional, but good for study)
      const { data: pagosData, error: pagosError } = await supabase
        .from('pagos_clientes')
        .select('*')
        .eq('cliente_id', currentClient.id);

      if (pagosError) {
        console.error('La tabla pagos_clientes no existe o falló:', pagosError);
      }

      setDocumentos(docData || []);
      setPagos(pagosData || []);
    } catch (err) {
      console.error(err);
      setError("Error: " + (err.message || err.details || err.hint || JSON.stringify(err)));
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!currentClient || !selectedPeriodo) return;
    setDownloadingPdf(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/pdf/report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cliente_id: currentClient.id, periodo: selectedPeriodo })
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'No se pudo generar el informe');
      }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Informe_${currentClient.ruc}_${selectedPeriodo}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert(err.message || 'Error al generar el informe PDF');
    } finally {
      setDownloadingPdf(false);
    }
  };

  if (!currentClient) {
    return (
      <div className="empty-state" style={{display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)'}}>
        <Activity size={48} style={{opacity: 0.5, marginBottom: '1rem'}} />
        <p>Selecciona un cliente para visualizar su Inteligencia Financiera</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="loading-container" style={{display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)'}}>
        <Loader2 className="animate-spin" size={40} style={{color: 'var(--accent-primary)', marginBottom: '1rem'}} />
        <p>Procesando datos financieros del periodo...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="empty-state" style={{ color: '#ef4444', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%'}}>
        <AlertCircle size={48} style={{marginBottom: '1rem'}} />
        <p>{error}</p>
      </div>
    );
  }

  // === CALCULATIONS (todo derivado de v_libro_unificado, sin datos simulados) ===

  // 1. KPIs
  const ventas = documentos.filter(d => d.libro !== 'COMPRAS');
  const compras = documentos.filter(d => d.libro === 'COMPRAS');

  const totalVentas = ventas.reduce((acc, curr) => acc + Number(curr.total_cp || 0), 0);
  const totalCompras = compras.reduce((acc, curr) => acc + Number(curr.total_cp || 0), 0);

  const igvVentas = ventas.reduce((acc, curr) => acc + Number(curr.igv || 0), 0);
  const igvCompras = compras.reduce((acc, curr) => acc + Number(curr.igv || 0), 0);
  const igvPagar = igvVentas - igvCompras; // Si es positivo, paga. Negativo, saldo a favor.

  // "Procesamiento Completo" — % de documentos que ya pasaron el enriquecimiento
  // IA (estado_enriquecimiento = 'COMPLETO'), el único campo de estado que
  // realmente existe en v_libro_unificado.
  const procesadosCompletos = documentos.filter(d => d.estado_enriquecimiento === 'COMPLETO').length;
  const tasaProcesamiento = documentos.length > 0 ? Math.round((procesadosCompletos / documentos.length) * 100) : 0;

  // 2. Evolución Diaria (Gráfico de Área)
  const dataDiariaMap = {};
  documentos.forEach(d => {
    const fecha = d.fecha_emision;
    if(!fecha) return;
    if(!dataDiariaMap[fecha]) {
      dataDiariaMap[fecha] = { fecha, ventas: 0, compras: 0 };
    }
    if (d.libro !== 'COMPRAS') {
      dataDiariaMap[fecha].ventas += Number(d.total_cp || 0);
    } else {
      dataDiariaMap[fecha].compras += Number(d.total_cp || 0);
    }
  });
  const evolucionDiaria = Object.values(dataDiariaMap).sort((a, b) => new Date(a.fecha) - new Date(b.fecha));

  // 3. Distribución de Compras por Tipo de Comprobante (dato real: tipo_cp_doc)
  const tipoComprobanteMap = {};
  compras.forEach(d => {
    const label = getTipoCpLabel(d.tipo_cp_doc);
    tipoComprobanteMap[label] = (tipoComprobanteMap[label] || 0) + Number(d.total_cp || 0);
  });
  const distribucionData = Object.entries(tipoComprobanteMap)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  // 4. Top 5 Clientes (ventas) y Top 5 Proveedores (compras), por separado
  const buildTopEntidades = (docs) => {
    const map = {};
    docs.forEach(d => {
      const nombre = d.nombre_tercero || 'Desconocido';
      map[nombre] = (map[nombre] || 0) + Number(d.total_cp || 0);
    });
    return Object.entries(map)
      .map(([nombre, monto]) => ({ nombre, monto }))
      .sort((a, b) => b.monto - a.monto)
      .slice(0, 5);
  };
  const topClientes = buildTopEntidades(ventas);
  const topProveedores = buildTopEntidades(compras);

  // 5. Balance del Periodo (Ventas vs Compras vs Utilidad Bruta)
  const utilidadBruta = totalVentas - totalCompras;
  const maxBalance = Math.max(totalVentas, totalCompras, Math.abs(utilidadBruta), 1);

  // 6. Documentos Observados — cualquiera que no haya completado el enriquecimiento IA
  const observados = documentos.filter(d => d.estado_enriquecimiento !== 'COMPLETO').slice(0, 50);

  const getObservadoBadgeStyle = (estado) => {
    if (estado === 'ERROR') return { bg: 'rgba(239,68,68,0.15)', color: '#f87171' };
    if (estado === 'PARCIAL') return { bg: 'rgba(245,158,11,0.15)', color: '#fbbf24' };
    return { bg: 'rgba(148,163,184,0.15)', color: '#94a3b8' }; // PENDIENTE / sin estado
  };

  return (
    <div className="bento-dashboard animate-fade-in" style={{padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%', overflowY: 'auto'}}>

      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end'}}>
        <div>
          <h2 style={{fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)', margin: 0}}>Resumen Financiero</h2>
          <p style={{color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem'}}>Dashboard analítico para {currentClient.razon_social} • {selectedPeriodo}</p>
        </div>
        <button className="btn btn-outline" onClick={handleDownloadPdf} disabled={downloadingPdf}>
          {downloadingPdf ? <Loader2 size={16} className="spin" /> : <Download size={16} />}
          {downloadingPdf ? 'Generando informe...' : 'Descargar Informe PDF'}
        </button>
      </div>

      {/* Grid Layout Principal */}
      <div className="bento-grid" style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gridAutoRows: 'minmax(120px, auto)',
        gap: '1.5rem'
      }}>

        {/* --- ROW 1: KPIs 1x1 --- */}
        <div className="glass-panel" style={{padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', gridColumn: 'span 1'}}>
          <div style={{color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <TrendingUp size={16} color="#10b981"/> Ventas Totales
          </div>
          <div style={{fontSize: '2rem', fontWeight: 700, color: 'var(--text-main)'}}>{formatCurrency(totalVentas)}</div>
          <div style={{fontSize: '0.8rem', color: '#10b981', display: 'flex', alignItems: 'center', gap: '0.25rem'}}><TrendingUp size={12}/> {ventas.length} doc(s)</div>
        </div>

        <div className="glass-panel" style={{padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', gridColumn: 'span 1'}}>
          <div style={{color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <TrendingDown size={16} color="#ef4444"/> Compras Totales
          </div>
          <div style={{fontSize: '2rem', fontWeight: 700, color: 'var(--text-main)'}}>{formatCurrency(totalCompras)}</div>
          <div style={{fontSize: '0.8rem', color: '#ef4444', display: 'flex', alignItems: 'center', gap: '0.25rem'}}><TrendingDown size={12}/> {compras.length} doc(s)</div>
        </div>

        <div className="glass-panel" style={{padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', gridColumn: 'span 1'}}>
          <div style={{color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <DollarSign size={16} color={igvPagar > 0 ? '#f59e0b' : '#3b82f6'}/> IGV Resultante
          </div>
          <div style={{fontSize: '2rem', fontWeight: 700, color: igvPagar > 0 ? '#f59e0b' : '#3b82f6'}}>
            {formatCurrency(Math.abs(igvPagar))}
          </div>
          <div style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>
            {igvPagar > 0 ? 'A pagar' : 'Saldo a favor'}
          </div>
        </div>

        <div className="glass-panel" style={{padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', gridColumn: 'span 1'}}>
          <div style={{color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <Activity size={16} color="#8b5cf6"/> Procesamiento Completo
          </div>
          <div style={{display: 'flex', alignItems: 'baseline', gap: '0.5rem'}}>
            <div style={{fontSize: '2rem', fontWeight: 700, color: 'var(--text-main)'}}>{tasaProcesamiento}%</div>
          </div>
          <div style={{width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden'}}>
            <div style={{width: `${tasaProcesamiento}%`, height: '100%', background: '#8b5cf6', borderRadius: '3px'}}></div>
          </div>
          <div style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>{procesadosCompletos} de {documentos.length} listos</div>
        </div>

        {/* --- ROW 2: Evolución + Distribución real + Balance --- */}
        <div className="glass-panel" style={{padding: '1.5rem', gridColumn: 'span 2', gridRow: 'span 2', display: 'flex', flexDirection: 'column'}}>
          <h3 style={{fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginTop: 0, marginBottom: '1.5rem'}}>Evolución de Movimientos Diarios</h3>
          <div style={{flex: 1, minHeight: '250px'}}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={evolucionDiaria} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorVentas" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorCompras" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255, 255, 255, 0.08)" />
                <XAxis dataKey="fecha" stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => val.substring(8, 10)} />
                <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `S/${val/1000}k`} width={50} />
                <Tooltip
                  contentStyle={{borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', boxShadow: '0 10px 25px rgba(0,0,0,0.5)', background: 'rgba(15,15,20,0.92)', color: '#f8fafc'}}
                  formatter={(value) => formatCurrency(value)}
                  labelFormatter={(label) => `Fecha: ${label}`}
                />
                <Legend verticalAlign="top" height={36}/>
                <Area type="monotone" dataKey="ventas" name="Ventas" stroke="#10b981" fillOpacity={1} fill="url(#colorVentas)" strokeWidth={2} />
                <Area type="monotone" dataKey="compras" name="Compras" stroke="#ef4444" fillOpacity={1} fill="url(#colorCompras)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel" style={{padding: '1.5rem', gridColumn: 'span 1', gridRow: 'span 2', display: 'flex', flexDirection: 'column'}}>
          <h3 style={{fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginTop: 0, marginBottom: '0'}}>Compras por Tipo de Comprobante</h3>
          <p style={{fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem'}}>Datos reales del periodo</p>
          <div style={{flex: 1, minHeight: '150px'}}>
            {distribucionData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={distribucionData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    stroke="none"
                  >
                    {distribucionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="none" />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value) => formatCurrency(value)}
                    contentStyle={{borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', boxShadow: '0 10px 25px rgba(0,0,0,0.5)', background: 'rgba(15,15,20,0.92)', color: '#f8fafc'}}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', fontSize: '0.85rem'}}>Sin compras en el periodo</div>
            )}
          </div>
          {/* Legend */}
          <div style={{display: 'flex', flexWrap: 'wrap', gap: '0.5rem', justifyContent: 'center'}}>
            {distribucionData.map((d, i) => (
              <div key={i} style={{display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.75rem', color: 'var(--text-muted)'}}>
                <div style={{width: '8px', height: '8px', borderRadius: '50%', background: COLORS[i % COLORS.length]}}></div>
                {d.name}
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel" style={{padding: '1.5rem', gridColumn: 'span 1', gridRow: 'span 2', display: 'flex', flexDirection: 'column'}}>
          <h3 style={{fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginTop: 0, marginBottom: '0'}}>Balance del Periodo</h3>
          <p style={{fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.5rem'}}>Ventas vs. Compras vs. Utilidad</p>
          <div style={{display: 'flex', flexDirection: 'column', gap: '1.25rem', flex: 1, justifyContent: 'center'}}>
            {[
              { label: 'Ventas', value: totalVentas, color: '#10b981', icon: <TrendingUp size={14} /> },
              { label: 'Compras', value: totalCompras, color: '#ef4444', icon: <TrendingDown size={14} /> },
              { label: 'Utilidad Bruta', value: utilidadBruta, color: utilidadBruta >= 0 ? '#3b82f6' : '#f59e0b', icon: <Scale size={14} /> },
            ].map((row, idx) => (
              <div key={idx}>
                <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem'}}>
                  <span style={{fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.35rem'}}>{row.icon} {row.label}</span>
                  <span style={{fontSize: '0.85rem', fontWeight: 700, fontFamily: 'monospace', color: row.color}}>{formatCurrency(row.value)}</span>
                </div>
                <div style={{width: '100%', height: '6px', background: 'rgba(255,255,255,0.08)', borderRadius: '3px', overflow: 'hidden'}}>
                  <div style={{width: `${Math.min(100, (Math.abs(row.value) / maxBalance) * 100)}%`, height: '100%', background: row.color, borderRadius: '3px'}}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* --- ROW 3: Top Clientes + Top Proveedores + Últimos Movimientos --- */}
        <div className="glass-panel" style={{padding: '1.5rem', gridColumn: 'span 1', gridRow: 'span 2', display: 'flex', flexDirection: 'column'}}>
          <h3 style={{fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginTop: 0, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem'}}>
            <Users size={16} color="#10b981" /> Top 5 Clientes
          </h3>
          <p style={{fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.5rem'}}>Mayor volumen en ventas</p>
          <div style={{display: 'flex', flexDirection: 'column', gap: '1rem', flex: 1, overflowY: 'auto'}}>
            {topClientes.map((ent, idx) => (
              <div key={idx} style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                <div style={{display: 'flex', alignItems: 'center', gap: '0.75rem'}}>
                  <div style={{width: '28px', height: '28px', borderRadius: '50%', background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', fontWeight: 600}}>
                    {idx + 1}
                  </div>
                  <div style={{fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '120px'}} title={ent.nombre}>
                    {ent.nombre}
                  </div>
                </div>
                <div style={{fontSize: '0.85rem', fontWeight: 700, fontFamily: 'monospace', color: 'var(--text-main)'}}>
                  {formatCurrency(ent.monto)}
                </div>
              </div>
            ))}
            {topClientes.length === 0 && <div style={{color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', marginTop: '2rem'}}>Sin ventas</div>}
          </div>
        </div>

        <div className="glass-panel" style={{padding: '1.5rem', gridColumn: 'span 1', gridRow: 'span 2', display: 'flex', flexDirection: 'column'}}>
          <h3 style={{fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginTop: 0, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem'}}>
            <ShoppingBag size={16} color="#ef4444" /> Top 5 Proveedores
          </h3>
          <p style={{fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.5rem'}}>Mayor volumen en compras</p>
          <div style={{display: 'flex', flexDirection: 'column', gap: '1rem', flex: 1, overflowY: 'auto'}}>
            {topProveedores.map((ent, idx) => (
              <div key={idx} style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                <div style={{display: 'flex', alignItems: 'center', gap: '0.75rem'}}>
                  <div style={{width: '28px', height: '28px', borderRadius: '50%', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', fontWeight: 600}}>
                    {idx + 1}
                  </div>
                  <div style={{fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '120px'}} title={ent.nombre}>
                    {ent.nombre}
                  </div>
                </div>
                <div style={{fontSize: '0.85rem', fontWeight: 700, fontFamily: 'monospace', color: 'var(--text-main)'}}>
                  {formatCurrency(ent.monto)}
                </div>
              </div>
            ))}
            {topProveedores.length === 0 && <div style={{color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', marginTop: '2rem'}}>Sin compras</div>}
          </div>
        </div>

        <div className="glass-panel" style={{padding: '1.5rem', gridColumn: 'span 2', gridRow: 'span 2', display: 'flex', flexDirection: 'column'}}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem'}}>
            <h3 style={{fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', margin: 0}}>Últimos Movimientos Registrados</h3>
          </div>
          <div style={{flex: 1, overflowY: 'auto', maxHeight: '300px', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px'}}>
            <table style={{width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem'}}>
              <thead style={{position: 'sticky', top: 0, background: '#0d0d12', zIndex: 1}}>
                <tr style={{textAlign: 'left', borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)'}}>
                  <th style={{padding: '0.75rem'}}>Fecha</th>
                  <th style={{padding: '0.75rem'}}>Tipo</th>
                  <th style={{padding: '0.75rem'}}>Entidad</th>
                  <th style={{padding: '0.75rem', textAlign: 'right'}}>Monto</th>
                </tr>
              </thead>
              <tbody>
                {documentos.slice(0, 50).map(d => (
                  <tr key={d.car_sunat || `${d.libro}-${d.nro_cp}-${d.fecha_emision}`} style={{borderBottom: '1px solid rgba(255,255,255,0.06)'}}>
                    <td style={{padding: '0.75rem', color: 'var(--text-muted)'}}>{d.fecha_emision}</td>
                    <td style={{padding: '0.75rem'}}>
                      <span style={{
                        padding: '2px 8px', borderRadius: '12px', fontSize: '0.7rem', fontWeight: 600,
                        background: d.libro !== 'COMPRAS' ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)',
                        color: d.libro !== 'COMPRAS' ? '#34d399' : '#f87171'
                      }}>
                        {d.libro !== 'COMPRAS' ? 'VENTA' : 'COMPRA'}
                      </span>
                    </td>
                    <td style={{padding: '0.75rem', fontWeight: 600, color: 'var(--text-main)', maxWidth: '150px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}} title={d.nombre_tercero}>
                      {d.nombre_tercero}
                    </td>
                    <td style={{padding: '0.75rem', textAlign: 'right', fontFamily: 'monospace', fontWeight: 600, color: 'var(--text-main)'}}>
                      {formatCurrency(d.total_cp)}
                    </td>
                  </tr>
                ))}
                {documentos.length === 0 && (
                  <tr><td colSpan="4" style={{textAlign: 'center', padding: '2rem', color: 'var(--text-muted)'}}>Sin movimientos en el periodo</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* --- ROW 4: Documentos Observados (ancho completo) --- */}
        <div className="glass-panel" style={{padding: '1.5rem', gridColumn: 'span 4', display: 'flex', flexDirection: 'column'}}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem'}}>
            <h3 style={{fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
              <AlertCircle size={18} color="#ef4444" /> Documentos con Procesamiento Incompleto
            </h3>
            <span style={{fontSize: '0.8rem', background: 'rgba(239,68,68,0.15)', color: '#f87171', padding: '2px 8px', borderRadius: '12px', fontWeight: 600}}>
              {observados.length} alertas
            </span>
          </div>
          <div style={{flex: 1, overflowY: 'auto', maxHeight: '300px', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px'}}>
            <table style={{width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem'}}>
              <thead style={{position: 'sticky', top: 0, background: '#0d0d12', zIndex: 1}}>
                <tr style={{textAlign: 'left', borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)'}}>
                  <th style={{padding: '0.75rem'}}>Comprobante</th>
                  <th style={{padding: '0.75rem'}}>Entidad</th>
                  <th style={{padding: '0.75rem', textAlign: 'center'}}>Estado</th>
                </tr>
              </thead>
              <tbody>
                {observados.map(d => {
                  const style = getObservadoBadgeStyle(d.estado_enriquecimiento);
                  return (
                    <tr key={d.car_sunat || `${d.libro}-${d.nro_cp}-${d.fecha_emision}`} style={{borderBottom: '1px solid rgba(255,255,255,0.06)'}}>
                      <td style={{padding: '0.75rem', fontWeight: 600, color: 'var(--text-main)', fontFamily: 'monospace'}}>
                        {getTipoCpLabel(d.tipo_cp_doc)}-{d.serie_cdp}-{d.nro_cp}
                      </td>
                      <td style={{padding: '0.75rem', color: 'var(--text-muted)', maxWidth: '200px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>
                        {d.nombre_tercero}
                      </td>
                      <td style={{padding: '0.75rem', textAlign: 'center'}}>
                        <span className="badge" style={{background: style.bg, color: style.color}}>
                          {ESTADO_LABELS[d.estado_enriquecimiento] || 'Pendiente'}
                        </span>
                      </td>
                    </tr>
                  )
                })}
                {observados.length === 0 && (
                  <tr>
                    <td colSpan="3" style={{textAlign: 'center', padding: '2rem', color: 'var(--text-muted)'}}>
                      <CheckCircle2 size={32} style={{opacity: 0.5, margin: '0 auto 0.5rem auto', color: '#10b981'}} />
                      Todos los comprobantes están procesados.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>

      {(userRole === 'admin' || userRole === 'accountant') && (
        <AttachmentsDropzone
          clienteId={currentClient.id}
          periodo={selectedPeriodo}
          apiBaseUrl={API_BASE_URL}
        />
      )}

    </div>
  );
}
