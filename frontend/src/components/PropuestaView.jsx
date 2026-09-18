import React, { useState, useEffect } from 'react';
import { DownloadCloud, Database, Search, FileText } from 'lucide-react';
import { supabase } from '../supabaseClient';

export default function PropuestaView({ currentClient, selectedPeriodo }) {
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
        console.error('Error fetching propuesta:', error);
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
    (r.nro_doc_identidad || '').includes(searchTerm) ||
    (r.nro_cp || '').includes(searchTerm)
  );

  return (
    <div className="view-container animate-fade-in" style={{padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%'}}>
      {/* Top Actions */}
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <div>
          <h2 style={{fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-main)', margin: 0}}>Propuesta SIRE</h2>
          <p style={{color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.25rem'}}>Gestiona y descarga la propuesta de comprobantes desde SUNAT.</p>
        </div>
        <div style={{display: 'flex', gap: '1rem'}}>
          <button className="btn btn-primary" style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <DownloadCloud size={16} /> Autenticar y Descargar Propuesta SIRE
          </button>
        </div>
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
          Propuesta Compras
        </button>
        <button 
          onClick={() => setTipo('ventas')}
          style={{
            background: 'none', border: 'none', padding: '0.5rem 1rem', fontWeight: 600, cursor: 'pointer',
            color: tipo === 'ventas' ? 'var(--accent-primary)' : 'var(--text-muted)',
            borderBottom: tipo === 'ventas' ? '2px solid var(--accent-primary)' : '2px solid transparent'
          }}
        >
          Propuesta Ventas
        </button>
      </div>

      {/* Table Section */}
      <div className="glass-panel data-panel" style={{flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden'}}>
        <div className="table-header-actions" style={{padding: '1rem', borderBottom: '1px solid rgba(226, 232, 240, 0.8)', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <div className="table-title" style={{display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: 'var(--text-main)'}}>
            <Database size={18} color="var(--accent-primary)" />
            Comprobantes de Propuesta ({filteredData.length})
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
            <div style={{textAlign: 'center', padding: '3rem', color: 'var(--text-muted)'}}>Seleccione un cliente y periodo para ver la propuesta.</div>
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
                  <th style={{padding: '0.75rem 0.5rem'}}>Tipo</th>
                  <th style={{padding: '0.75rem 0.5rem'}}>Serie-Nro</th>
                  <th style={{padding: '0.75rem 0.5rem'}}>RUC Doc.</th>
                  <th style={{padding: '0.75rem 0.5rem'}}>Razón Social</th>
                  <th style={{padding: '0.75rem 0.5rem', textAlign: 'right'}}>Base Imp.</th>
                  <th style={{padding: '0.75rem 0.5rem', textAlign: 'right'}}>IGV</th>
                  <th style={{padding: '0.75rem 0.5rem', textAlign: 'right'}}>Total</th>
                </tr>
              </thead>
              <tbody>
                {filteredData.map((row) => (
                  <tr key={row.id} style={{borderBottom: '1px solid rgba(255,255,255,0.06)'}}>
                    <td style={{padding: '0.75rem 0.5rem'}}>{row.fecha_emision}</td>
                    <td style={{padding: '0.75rem 0.5rem'}}>{row.tipo_cp_doc}</td>
                    <td style={{padding: '0.75rem 0.5rem'}}>{row.serie_cdp}-{row.nro_cp}</td>
                    <td style={{padding: '0.75rem 0.5rem'}}>{row.nro_doc_identidad}</td>
                    <td style={{padding: '0.75rem 0.5rem', maxWidth: '200px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}} title={row.razon_social}>
                      {row.razon_social}
                    </td>
                    <td style={{padding: '0.75rem 0.5rem', textAlign: 'right', fontFamily: 'monospace'}}>
                      {Number(row.bi_gravado_dg || 0).toFixed(2)}
                    </td>
                    <td style={{padding: '0.75rem 0.5rem', textAlign: 'right', fontFamily: 'monospace'}}>
                      {Number(row.igv_ipm_dg || 0).toFixed(2)}
                    </td>
                    <td style={{padding: '0.75rem 0.5rem', textAlign: 'right', fontFamily: 'monospace', fontWeight: 600}}>
                      {Number(row.total_cp || 0).toFixed(2)}
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
