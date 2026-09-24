import { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import {
  TrendingUp, TrendingDown, Loader2, AlertCircle, Users, Scale,
  ShoppingBag, Building2, CheckCircle2
} from 'lucide-react';
import { supabase } from '../supabaseClient';
import './DashboardView.css';

const formatCurrency = (value) => {
  return new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' }).format(value || 0);
};

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

const ESTADO_COLORS = {
  DESCARGADO: '#10b981',
  PENDIENTE: '#f59e0b',
  NO_EXISTE: '#64748b',
  NO_DESCARGABLE: '#ef4444',
  ERROR: '#ef4444',
};

// Fetch every row of a table/query, paginating past Supabase's 1000-row cap —
// a period can hold several thousand comprobantes across all clients.
const fetchAllRows = async (table, selectQuery, filters = {}) => {
  let allData = [];
  let page = 0;
  const pageSize = 1000;
  let fetchMore = true;

  while (fetchMore) {
    let query = supabase.from(table).select(selectQuery).range(page * pageSize, (page + 1) * pageSize - 1);
    Object.keys(filters).forEach((key) => {
      query = query.eq(key, filters[key]);
    });
    const { data, error } = await query;
    if (error) {
      console.error(`Error fetching ${table}:`, error);
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

export default function AdminOverviewView({ selectedPeriodo }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [documentos, setDocumentos] = useState([]);
  const [fisicos, setFisicos] = useState([]);

  useEffect(() => {
    if (selectedPeriodo) {
      loadData();
    }
  }, [selectedPeriodo]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [docData, fisicosData] = await Promise.all([
        fetchAllRows(
          'v_libro_unificado',
          'ruc, cliente, libro, fecha_emision, total_cp, igv, tipo_cp_doc, estado_enriquecimiento',
          { periodo: selectedPeriodo }
        ),
        fetchAllRows(
          'sire_comprobantes_fisicos',
          'estado_xml, clientes(ruc, razon_social)',
          { periodo: selectedPeriodo }
        ),
      ]);
      setDocumentos(docData || []);
      setFisicos(fisicosData || []);
    } catch (err) {
      console.error(err);
      setError('Error: ' + (err.message || JSON.stringify(err)));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
        <Loader2 className="animate-spin" size={40} style={{ color: 'var(--accent-primary)', marginBottom: '1rem' }} />
        <p>Consolidando datos de todos los clientes...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="empty-state" style={{ color: '#ef4444', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
        <AlertCircle size={48} style={{ marginBottom: '1rem' }} />
        <p>{error}</p>
      </div>
    );
  }

  // === CALCULATIONS ===

  const ventas = documentos.filter((d) => d.libro !== 'COMPRAS');
  const compras = documentos.filter((d) => d.libro === 'COMPRAS');
  const totalVentas = ventas.reduce((acc, d) => acc + Number(d.total_cp || 0), 0);
  const totalCompras = compras.reduce((acc, d) => acc + Number(d.total_cp || 0), 0);
  const igvVentas = ventas.reduce((acc, d) => acc + Number(d.igv || 0), 0);
  const igvCompras = compras.reduce((acc, d) => acc + Number(d.igv || 0), 0);
  const igvPagar = igvVentas - igvCompras;
  const utilidadBruta = totalVentas - totalCompras;
  const maxBalance = Math.max(totalVentas, totalCompras, Math.abs(utilidadBruta), 1);

  const clientesConMovimiento = new Set(documentos.map((d) => d.ruc)).size;

  // Descarga XML: completitud global + distribución de estados
  const totalFisicos = fisicos.length;
  const descargados = fisicos.filter((f) => f.estado_xml === 'DESCARGADO').length;
  const pctCompletitudGlobal = totalFisicos > 0 ? Math.round((descargados / totalFisicos) * 100) : 0;

  const estadoMap = {};
  fisicos.forEach((f) => {
    const estado = f.estado_xml || 'PENDIENTE';
    estadoMap[estado] = (estadoMap[estado] || 0) + 1;
  });
  const estadoData = Object.entries(estadoMap).map(([name, value]) => ({ name, value }));

  // Ranking de completitud por cliente (peor primero, para detectar atrasos)
  const porClienteMap = {};
  fisicos.forEach((f) => {
    const razon = f.clientes?.razon_social || 'Desconocido';
    if (!porClienteMap[razon]) {
      porClienteMap[razon] = { cliente: razon, total: 0, descargados: 0 };
    }
    porClienteMap[razon].total += 1;
    if (f.estado_xml === 'DESCARGADO') porClienteMap[razon].descargados += 1;
  });
  const rankingCompletitud = Object.values(porClienteMap)
    .map((c) => ({ ...c, pct: c.total > 0 ? Math.round((c.descargados / c.total) * 100) : 0 }))
    .sort((a, b) => a.pct - b.pct)
    .slice(0, 15);

  // Evolución diaria global
  const dataDiariaMap = {};
  documentos.forEach((d) => {
    const fecha = d.fecha_emision;
    if (!fecha) return;
    if (!dataDiariaMap[fecha]) dataDiariaMap[fecha] = { fecha, ventas: 0, compras: 0 };
    if (d.libro !== 'COMPRAS') dataDiariaMap[fecha].ventas += Number(d.total_cp || 0);
    else dataDiariaMap[fecha].compras += Number(d.total_cp || 0);
  });
  const evolucionDiaria = Object.values(dataDiariaMap).sort((a, b) => new Date(a.fecha) - new Date(b.fecha));

  // Top clientes propios por ventas / compras (no por contraparte)
  const buildTopClientesPropios = (docs) => {
    const map = {};
    docs.forEach((d) => {
      const nombre = d.cliente || 'Desconocido';
      map[nombre] = (map[nombre] || 0) + Number(d.total_cp || 0);
    });
    return Object.entries(map)
      .map(([nombre, monto]) => ({ nombre, monto }))
      .sort((a, b) => b.monto - a.monto)
      .slice(0, 5);
  };
  const topVentas = buildTopClientesPropios(ventas);
  const topCompras = buildTopClientesPropios(compras);

  const rankingBarColor = (pct) => (pct >= 90 ? '#10b981' : pct >= 60 ? '#f59e0b' : '#ef4444');

  return (
    <div className="bento-dashboard animate-fade-in" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%', overflowY: 'auto' }}>
      <div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>Resumen General</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>Vista consolidada de todos los clientes • {selectedPeriodo}</p>
      </div>

      <div className="bento-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gridAutoRows: 'minmax(120px, auto)', gap: '1.5rem' }}>

        {/* --- ROW 1: KPIs --- */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', gridColumn: 'span 1' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Building2 size={16} color="#3b82f6" /> Clientes con Movimiento
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--text-main)' }}>{clientesConMovimiento}</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{documentos.length} comprobante(s) en el periodo</div>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', gridColumn: 'span 1' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <TrendingUp size={16} color="#10b981" /> Ventas Totales
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--text-main)' }}>{formatCurrency(totalVentas)}</div>
          <div style={{ fontSize: '0.8rem', color: '#10b981' }}>{ventas.length} doc(s)</div>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', gridColumn: 'span 1' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <TrendingDown size={16} color="#ef4444" /> Compras Totales
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--text-main)' }}>{formatCurrency(totalCompras)}</div>
          <div style={{ fontSize: '0.8rem', color: '#ef4444' }}>{compras.length} doc(s)</div>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', gridColumn: 'span 1' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CheckCircle2 size={16} color="#8b5cf6" /> Completitud Descarga
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--text-main)' }}>{pctCompletitudGlobal}%</div>
          <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
            <div style={{ width: `${pctCompletitudGlobal}%`, height: '100%', background: '#8b5cf6', borderRadius: '3px' }}></div>
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{descargados} de {totalFisicos} XML descargados</div>
        </div>

        {/* --- ROW 2: Evolución + Estados de descarga + Balance --- */}
        <div className="glass-panel" style={{ padding: '1.5rem', gridColumn: 'span 2', gridRow: 'span 2', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginTop: 0, marginBottom: '1.5rem' }}>Evolución de Movimientos Diarios (Todos los Clientes)</h3>
          <div style={{ flex: 1, minHeight: '250px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={evolucionDiaria} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorVentasGen" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorComprasGen" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255, 255, 255, 0.08)" />
                <XAxis dataKey="fecha" stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => val.substring(8, 10)} />
                <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `S/${val / 1000}k`} width={50} />
                <Tooltip
                  contentStyle={{ borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', boxShadow: '0 10px 25px rgba(0,0,0,0.5)', background: 'rgba(15,15,20,0.92)', color: '#f8fafc' }}
                  formatter={(value) => formatCurrency(value)}
                  labelFormatter={(label) => `Fecha: ${label}`}
                />
                <Legend verticalAlign="top" height={36} />
                <Area type="monotone" dataKey="ventas" name="Ventas" stroke="#10b981" fillOpacity={1} fill="url(#colorVentasGen)" strokeWidth={2} />
                <Area type="monotone" dataKey="compras" name="Compras" stroke="#ef4444" fillOpacity={1} fill="url(#colorComprasGen)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', gridColumn: 'span 1', gridRow: 'span 2', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginTop: 0, marginBottom: '0' }}>Estado de Descarga (XML)</h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>{totalFisicos} comprobante(s) físicos</p>
          <div style={{ flex: 1, minHeight: '150px' }}>
            {estadoData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={estadoData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value" stroke="none">
                    {estadoData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={ESTADO_COLORS[entry.name] || COLORS[index % COLORS.length]} stroke="none" />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', boxShadow: '0 10px 25px rgba(0,0,0,0.5)', background: 'rgba(15,15,20,0.92)', color: '#f8fafc' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', fontSize: '0.85rem' }}>Sin comprobantes físicos</div>
            )}
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', justifyContent: 'center' }}>
            {estadoData.map((d, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: ESTADO_COLORS[d.name] || COLORS[i % COLORS.length] }}></div>
                {d.name} ({d.value})
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', gridColumn: 'span 1', gridRow: 'span 2', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginTop: 0, marginBottom: '0' }}>Balance del Periodo</h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>Todos los clientes</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', flex: 1, justifyContent: 'center' }}>
            {[
              { label: 'Ventas', value: totalVentas, color: '#10b981', icon: <TrendingUp size={14} /> },
              { label: 'Compras', value: totalCompras, color: '#ef4444', icon: <TrendingDown size={14} /> },
              { label: 'Utilidad Bruta', value: utilidadBruta, color: utilidadBruta >= 0 ? '#3b82f6' : '#f59e0b', icon: <Scale size={14} /> },
              { label: igvPagar > 0 ? 'IGV a Pagar' : 'IGV Saldo a Favor', value: Math.abs(igvPagar), color: igvPagar > 0 ? '#f59e0b' : '#3b82f6', icon: <Scale size={14} /> },
            ].map((row, idx) => (
              <div key={idx}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>{row.icon} {row.label}</span>
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, fontFamily: 'monospace', color: row.color }}>{formatCurrency(row.value)}</span>
                </div>
                <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.08)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ width: `${Math.min(100, (Math.abs(row.value) / maxBalance) * 100)}%`, height: '100%', background: row.color, borderRadius: '3px' }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* --- ROW 3: Ranking de completitud + Top clientes ventas/compras --- */}
        <div className="glass-panel" style={{ padding: '1.5rem', gridColumn: 'span 2', gridRow: 'span 2', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginTop: 0, marginBottom: '0' }}>Ranking de Completitud por Cliente</h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>Los más atrasados primero</p>
          <div style={{ flex: 1, minHeight: '280px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={rankingCompletitud} layout="vertical" margin={{ top: 0, right: 20, left: 10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgba(255, 255, 255, 0.08)" />
                <XAxis type="number" domain={[0, 100]} stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v) => `${v}%`} />
                <YAxis type="category" dataKey="cliente" stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} width={140} />
                <Tooltip
                  contentStyle={{ borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', boxShadow: '0 10px 25px rgba(0,0,0,0.5)', background: 'rgba(15,15,20,0.92)', color: '#f8fafc' }}
                  formatter={(value, name, props) => [`${value}% (${props.payload.descargados}/${props.payload.total})`, 'Completitud']}
                />
                <Bar dataKey="pct" radius={[0, 4, 4, 0]}>
                  {rankingCompletitud.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={rankingBarColor(entry.pct)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', gridColumn: 'span 1', gridRow: 'span 2', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginTop: 0, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Users size={16} color="#10b981" /> Top 5 en Ventas
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>Clientes con mayor facturación</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', flex: 1, overflowY: 'auto' }}>
            {topVentas.map((ent, idx) => (
              <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', fontWeight: 600 }}>
                    {idx + 1}
                  </div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '120px' }} title={ent.nombre}>
                    {ent.nombre}
                  </div>
                </div>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, fontFamily: 'monospace', color: 'var(--text-main)' }}>{formatCurrency(ent.monto)}</div>
              </div>
            ))}
            {topVentas.length === 0 && <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', marginTop: '2rem' }}>Sin ventas</div>}
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', gridColumn: 'span 1', gridRow: 'span 2', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginTop: 0, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <ShoppingBag size={16} color="#ef4444" /> Top 5 en Compras
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>Clientes con mayor gasto</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', flex: 1, overflowY: 'auto' }}>
            {topCompras.map((ent, idx) => (
              <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', fontWeight: 600 }}>
                    {idx + 1}
                  </div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '120px' }} title={ent.nombre}>
                    {ent.nombre}
                  </div>
                </div>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, fontFamily: 'monospace', color: 'var(--text-main)' }}>{formatCurrency(ent.monto)}</div>
              </div>
            ))}
            {topCompras.length === 0 && <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', marginTop: '2rem' }}>Sin compras</div>}
          </div>
        </div>
      </div>
    </div>
  );
}
