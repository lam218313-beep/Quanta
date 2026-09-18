import React, { useState, useEffect } from 'react';
import { Search, BarChart3, Database, FileText, CheckCircle2, AlertCircle, Clock } from 'lucide-react';
import { supabase } from '../supabaseClient';

export default function ProcesamientoView({ currentClient, selectedPeriodo, userRole }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [tipo, setTipo] = useState('compras'); // 'compras' or 'ventas'

  useEffect(() => {
    const fetchData = async () => {
      if (!currentClient || !selectedPeriodo) {
        setData([]);
        return;
      }
      setLoading(true);
      
      const tableName = tipo === 'compras' ? 'sire_preliminar_compras' : 'sire_preliminar_ventas';
      const { data: fetchResult, error } = await supabase
        .from(tableName)
        .select('*')
        .eq('cliente_id', currentClient.id)
        .eq('periodo', selectedPeriodo);
        
      if (error) {
        console.error('Error fetching procesamiento data:', error);
        setData([]);
      } else {
        setData(fetchResult || []);
      }
      setLoading(false);
    };

    fetchData();
  }, [currentClient, selectedPeriodo, tipo]);

  const filteredData = data.filter(r => 
    (r.razon_social?.toLowerCase() || '').includes(searchTerm.toLowerCase()) || 
    (r.descripcion_comprobante?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
    (r.nro_cp || '').includes(searchTerm)
  );

  const getEstadoBadge = (estado) => {
    if (estado === 'COMPLETADO') return <span className="badge" style={{background: 'rgba(16,185,129,0.15)', color: '#34d399', display: 'flex', alignItems: 'center', gap: '0.25rem'}}><CheckCircle2 size={12}/> Completado</span>;
    if (estado === 'ERROR') return <span className="badge" style={{background: 'rgba(239,68,68,0.15)', color: '#f87171', display: 'flex', alignItems: 'center', gap: '0.25rem'}}><AlertCircle size={12}/> Error</span>;
    return <span className="badge" style={{background: 'rgba(245,158,11,0.15)', color: '#fbbf24', display: 'flex', alignItems: 'center', gap: '0.25rem'}}><Clock size={12}/> Pendiente</span>;
  };

  return (
    <div className="view-container animate-fade-in" style={{padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%'}}>
      {/* Top Actions */}
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <div>
          <h2 style={{fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-main)', margin: 0}}>Procesamiento IA</h2>
          <p style={{color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.25rem'}}>Análisis inteligente, extracción de glosas de XML y clasificación contable.</p>
        </div>
        {userRole !== 'client' && (
          <div style={{display: 'flex', gap: '1rem'}}>
            <button className="btn btn-outline" style={{display: 'flex', alignItems: 'center', gap: '0.5rem', borderColor: 'var(--accent-primary)', color: 'var(--accent-primary)'}}>
              <Search size={16} /> Extraer Glosas de XML
            </button>
            <button className="btn btn-primary" style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
              <BarChart3 size={16} /> Clasificar con Inteligencia Artificial
            </button>
          </div>
        )}
      </div>

      {/* Tabs / Toggle */}
      <div style={{display: 'flex', gap: '1rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '0.5rem'}}>
        <button 
          onClick={() => setTipo('compras')}
          style={{
            background: 'none', border: 'none', padding: '0.5rem 1rem', fontWeight: 600, cursor: 'pointer',
            color: tipo === 'compras' ? 'var(--accent-primary)' : 'var(--text-muted)',
            borderBottom: tipo === 'compras' ? '2px solid var(--accent-primary)' : '2px solid transparent'
          }}
        >
          Procesar Compras
        </button>
        <button 
          onClick={() => setTipo('ventas')}
          style={{
            background: 'none', border: 'none', padding: '0.5rem 1rem', fontWeight: 600, cursor: 'pointer',
            color: tipo === 'ventas' ? 'var(--accent-primary)' : 'var(--text-muted)',
            borderBottom: tipo === 'ventas' ? '2px solid var(--accent-primary)' : '2px solid transparent'
          }}
        >
          Procesar Ventas
        </button>
      </div>

      {/* Table Section */}
      <div className="glass-panel data-panel" style={{flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden'}}>
        <div className="table-header-actions" style={{padding: '1rem', borderBottom: '1px solid rgba(226, 232, 240, 0.8)', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <div className="table-title" style={{display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: 'var(--text-main)'}}>
            <Database size={18} color="var(--accent-primary)" />
            Resultados de Clasificación ({filteredData.length})
          </div>
          
          <div className="search-box" style={{width: '250px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', display: 'flex', alignItems: 'center', padding: '0.4rem 0.8rem'}}>
            <Search size={14} color="var(--text-muted)" style={{marginRight: '0.5rem'}} />
            <input 
              type="text" 
              placeholder="Buscar (Glosa, RUC, Nro)..." 
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
            <div style={{textAlign: 'center', padding: '3rem', color: 'var(--text-muted)'}}>Seleccione un cliente y periodo para ver el procesamiento.</div>
          ) : filteredData.length === 0 ? (
            <div style={{textAlign: 'center', padding: '3rem', color: 'var(--text-muted)'}}>
              <FileText size={48} style={{opacity: 0.3, margin: '0 auto 1rem auto', display: 'block'}} />
              No hay datos para procesar en este periodo.
            </div>
          ) : (
            <table style={{width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem'}}>
              <thead>
                <tr style={{textAlign: 'left', borderBottom: '2px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)'}}>
                  <th style={{padding: '0.75rem 0.5rem', width: '15%'}}>Comprobante</th>
                  <th style={{padding: '0.75rem 0.5rem', width: '15%'}}>{tipo === 'compras' ? 'Proveedor' : 'Cliente'}</th>
                  <th style={{padding: '0.75rem 0.5rem', width: '25%'}}>Glosa (Descripción XML)</th>
                  <th style={{padding: '0.75rem 0.5rem', width: '15%'}}>Categoría IA</th>
                  <th style={{padding: '0.75rem 0.5rem', width: '15%'}}>Cuenta Contable</th>
                  <th style={{padding: '0.75rem 0.5rem', textAlign: 'center', width: '15%'}}>Estado</th>
                </tr>
              </thead>
              <tbody>
                {filteredData.map((row) => (
                  <tr key={row.id} style={{borderBottom: '1px solid rgba(255,255,255,0.06)'}}>
                    <td style={{padding: '0.75rem 0.5rem'}}>
                      <div style={{fontFamily: 'monospace', fontWeight: 600, color: 'var(--text-main)'}}>{row.serie_cdp}-{row.nro_cp}</div>
                      <div style={{fontSize: '0.75rem', color: 'var(--text-muted)'}}>{row.fecha_emision}</div>
                    </td>
                    <td style={{padding: '0.75rem 0.5rem'}}>
                      <div style={{fontWeight: 600, color: 'var(--text-main)'}}>{row.nro_doc_identidad}</div>
                      <div style={{fontSize: '0.75rem', color: 'var(--text-muted)', maxWidth: '150px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}} title={row.razon_social}>
                        {row.razon_social}
                      </div>
                    </td>
                    <td style={{padding: '0.75rem 0.5rem'}}>
                      <div style={{fontSize: '0.8rem', color: row.descripcion_comprobante ? 'var(--text-main)' : '#94a3b8', fontStyle: row.descripcion_comprobante ? 'normal' : 'italic'}}>
                        {row.descripcion_comprobante || 'Pendiente de extracción...'}
                      </div>
                    </td>
                    <td style={{padding: '0.75rem 0.5rem'}}>
                      {row.categoria ? (
                        <span style={{padding: '0.2rem 0.5rem', background: 'rgba(255,255,255,0.06)', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.1)', fontSize: '0.75rem', fontWeight: 600, color: '#cbd5e1'}}>
                          {row.categoria}
                        </span>
                      ) : (
                        <span style={{color: '#cbd5e1'}}>-</span>
                      )}
                    </td>
                    <td style={{padding: '0.75rem 0.5rem'}}>
                      {row.cuenta_contable ? (
                        <div style={{display: 'flex', flexDirection: 'column'}}>
                          <span style={{fontFamily: 'monospace', fontWeight: 600, color: 'var(--accent-primary)'}}>{row.cuenta_contable}</span>
                          <span style={{fontSize: '0.7rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '150px'}} title={row.descripcion_cuenta}>
                            {row.descripcion_cuenta}
                          </span>
                        </div>
                      ) : (
                        <span style={{color: '#cbd5e1'}}>-</span>
                      )}
                    </td>
                    <td style={{padding: '0.75rem 0.5rem', textAlign: 'center'}}>
                      <div style={{display: 'flex', justifyContent: 'center'}}>
                        {getEstadoBadge(row.estado_enriquecimiento)}
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
