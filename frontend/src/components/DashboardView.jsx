import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import { 
  TrendingUp, TrendingDown, DollarSign, Activity, FileText, 
  Loader2, AlertCircle, CheckCircle2, XCircle, Users
} from 'lucide-react';
import { supabase } from '../supabaseClient';
import './DashboardView.css';

const formatCurrency = (value) => {
  return new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' }).format(value || 0);
};

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function DashboardView({ currentClient, selectedPeriodo }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Data states
  const [documentos, setDocumentos] = useState([]);
  const [pagos, setPagos] = useState([]);

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

  // === CALCULATIONS ===

  // 1. KPIs
  const ventas = documentos.filter(d => d.libro !== 'COMPRAS');
  const compras = documentos.filter(d => d.libro === 'COMPRAS');

  const totalVentas = ventas.reduce((acc, curr) => acc + Number(curr.total_cp || 0), 0);
  const totalCompras = compras.reduce((acc, curr) => acc + Number(curr.total_cp || 0), 0);
  
  const igvVentas = ventas.reduce((acc, curr) => acc + Number(curr.igv || 0), 0);
  const igvCompras = compras.reduce((acc, curr) => acc + Number(curr.igv || 0), 0);
  const igvPagar = igvVentas - igvCompras; // Si es positivo, paga. Negativo, saldo a favor.

  const digitalizados = documentos.filter(d => d.estado_pdf === 'Completado' && d.estado_xml === 'Completado').length;
  const tasaDigitalizacion = documentos.length > 0 ? Math.round((digitalizados / documentos.length) * 100) : 0;

  // 2. Evolución Diaria (Gráfico Lineal)
  // Agrupar por fecha
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

  // 3. Distribución (Mock: Categórico basado en Compras)
  // Como no tenemos clasificación IA explícita en esta vista, simularemos basado en proveedores frecuentes
  const distribucionData = [
    { name: 'Mercadería', value: totalCompras * 0.4 },
    { name: 'Servicios', value: totalCompras * 0.3 },
    { name: 'Planilla', value: totalCompras * 0.2 },
    { name: 'Otros', value: totalCompras * 0.1 },
  ];

  // 4. Top 5 Entidades
  const entidadesMap = {};
  documentos.forEach(d => {
    const nombre = d.nombre_tercero || 'Desconocido';
    if(!entidadesMap[nombre]) entidadesMap[nombre] = 0;
    entidadesMap[nombre] += Number(d.total_cp || 0);
  });
  const topEntidades = Object.entries(entidadesMap)
    .map(([nombre, monto]) => ({ nombre, monto }))
    .sort((a, b) => b.monto - a.monto)
    .slice(0, 5);

  // 5. Documentos Observados
  const observados = documentos.filter(d => d.estado_pdf !== 'Completado' || d.estado_xml !== 'Completado').slice(0, 50); // limit for UI

  return (
    <div className="bento-dashboard animate-fade-in" style={{padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%', overflowY: 'auto'}}>
      
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end'}}>
        <div>
          <h2 style={{fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)', margin: 0}}>Resumen Financiero</h2>
          <p style={{color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem'}}>Dashboard analítico para {currentClient.razon_social} • {selectedPeriodo}</p>
        </div>
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
            <Activity size={16} color="#8b5cf6"/> Digitalización
          </div>
          <div style={{display: 'flex', alignItems: 'baseline', gap: '0.5rem'}}>
            <div style={{fontSize: '2rem', fontWeight: 700, color: 'var(--text-main)'}}>{tasaDigitalizacion}%</div>
          </div>
          <div style={{width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden'}}>
            <div style={{width: `${tasaDigitalizacion}%`, height: '100%', background: '#8b5cf6', borderRadius: '3px'}}></div>
          </div>
          <div style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>{digitalizados} de {documentos.length} listos</div>
        </div>

        {/* --- ROW 2: Charts (2x2 Horizontal + 1x2 Vertical) --- */}
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
          <h3 style={{fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginTop: 0, marginBottom: '0.5rem'}}>Top 5 Entidades</h3>
          <p style={{fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.5rem'}}>Mayor volumen transaccional</p>
          <div style={{display: 'flex', flexDirection: 'column', gap: '1rem', flex: 1, overflowY: 'auto'}}>
            {topEntidades.map((ent, idx) => (
              <div key={idx} style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                <div style={{display: 'flex', alignItems: 'center', gap: '0.75rem'}}>
                  <div style={{width: '28px', height: '28px', borderRadius: '50%', background: 'rgba(59, 130, 246, 0.1)', color: '#3b82f6', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', fontWeight: 600}}>
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
            {topEntidades.length === 0 && <div style={{color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', marginTop: '2rem'}}>Sin movimientos</div>}
          </div>
        </div>

        <div className="glass-panel" style={{padding: '1.5rem', gridColumn: 'span 1', gridRow: 'span 2', display: 'flex', flexDirection: 'column'}}>
          <h3 style={{fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginTop: 0, marginBottom: '0'}}>Distribución de Gastos</h3>
          <p style={{fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem'}}>Simulación IA</p>
          <div style={{flex: 1, minHeight: '150px'}}>
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
          </div>
          {/* Legend */}
          <div style={{display: 'flex', flexWrap: 'wrap', gap: '0.5rem', justifyContent: 'center'}}>
            {distribucionData.map((d, i) => (
              <div key={i} style={{display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.75rem', color: 'var(--text-muted)'}}>
                <div style={{width: '8px', height: '8px', borderRadius: '50%', background: COLORS[i]}}></div>
                {d.name}
              </div>
            ))}
          </div>
        </div>

        {/* --- ROW 3: Tables --- */}
        
        {/* Tabla Movimientos Recientes */}
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
                  <tr key={d.id} style={{borderBottom: '1px solid rgba(255,255,255,0.06)'}}>
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
              </tbody>
            </table>
          </div>
        </div>

        {/* Tabla Documentos Observados */}
        <div className="glass-panel" style={{padding: '1.5rem', gridColumn: 'span 2', gridRow: 'span 2', display: 'flex', flexDirection: 'column'}}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem'}}>
            <h3 style={{fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
              <AlertCircle size={18} color="#ef4444" /> Documentos Incompletos / Observados
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
                  <th style={{padding: '0.75rem', textAlign: 'center'}}>Problema</th>
                </tr>
              </thead>
              <tbody>
                {observados.map(d => {
                  const faltaPDF = d.estado_pdf !== 'Completado';
                  const faltaXML = d.estado_xml !== 'Completado';
                  
                  return (
                    <tr key={d.id} style={{borderBottom: '1px solid rgba(255,255,255,0.06)'}}>
                      <td style={{padding: '0.75rem', fontWeight: 600, color: 'var(--text-main)', fontFamily: 'monospace'}}>
                        {d.tipo_comprobante}-{d.serie_comprobante}-{d.numero_comprobante}
                      </td>
                      <td style={{padding: '0.75rem', color: 'var(--text-muted)', maxWidth: '120px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>
                        {d.nombre_tercero}
                      </td>
                      <td style={{padding: '0.75rem', textAlign: 'center'}}>
                        <div style={{display: 'flex', gap: '0.5rem', justifyContent: 'center'}}>
                          {faltaPDF && <span className="badge" style={{background: 'rgba(239,68,68,0.15)', color: '#f87171', fontSize: '0.7rem'}}>Falta PDF</span>}
                          {faltaXML && <span className="badge" style={{background: 'rgba(245,158,11,0.15)', color: '#fbbf24', fontSize: '0.7rem'}}>Falta XML</span>}
                        </div>
                      </td>
                    </tr>
                  )
                })}
                {observados.length === 0 && (
                  <tr>
                    <td colSpan="3" style={{textAlign: 'center', padding: '2rem', color: 'var(--text-muted)'}}>
                      <CheckCircle2 size={32} style={{opacity: 0.5, margin: '0 auto 0.5rem auto', color: '#10b981'}} />
                      Todos los comprobantes están en regla.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
}
