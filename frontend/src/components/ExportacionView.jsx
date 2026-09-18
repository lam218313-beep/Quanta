import React, { useState, useEffect } from 'react';
import { Download, Database, Search, File, Eye, CheckCircle2, ChevronRight, FileText, Loader2 } from 'lucide-react';
import { supabase } from '../supabaseClient';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://quanta-production-07d7.up.railway.app';

export default function ExportacionView({ currentClient, selectedPeriodo }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [downloadingAction, setDownloadingAction] = useState(null); // null | 'pdf-compras' | 'pdf-ventas' | 'excel-preliminar' | 'excel-final'

  useEffect(() => {
    const fetchData = async () => {
      if (!currentClient || !selectedPeriodo) {
        setData([]);
        setSelectedDoc(null);
        return;
      }
      setLoading(true);
      
      const { data: fetchResult, error } = await supabase
        .from('v_libro_unificado')
        .select('*')
        .eq('ruc', currentClient.ruc)
        .eq('periodo', selectedPeriodo);
        
      if (error) {
        console.error('Error fetching exportacion data:', error);
        setData([]);
      } else {
        setData(fetchResult || []);
      }
      setLoading(false);
    };

    fetchData();
  }, [currentClient, selectedPeriodo]);

  const filteredData = data.filter(r =>
    (r.nombre_tercero?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
    (r.ruc_tercero || '').includes(searchTerm) ||
    (r.nro_cp || '').includes(searchTerm)
  );

  const downloadBlob = (blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  };

  const runExport = async (action, url, options, filename) => {
    if (!currentClient || !selectedPeriodo) {
      alert('Selecciona un cliente y un periodo primero.');
      return;
    }
    setDownloadingAction(action);
    try {
      const res = await fetch(url, options);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'No se pudo generar el archivo.');
      }
      const blob = await res.blob();
      downloadBlob(blob, filename);
    } catch (err) {
      console.error(err);
      alert(err.message || 'Error al generar el archivo.');
    } finally {
      setDownloadingAction(null);
    }
  };

  const handleConsolidarPdf = (tipoLibro) => {
    const action = tipoLibro === 'COMPRAS' ? 'pdf-compras' : 'pdf-ventas';
    runExport(
      action,
      `${API_BASE_URL}/api/export/pdf-merged`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ruc: currentClient.ruc, periodo: selectedPeriodo, tipo_libro: tipoLibro, allow_incomplete: false })
      },
      `Comprobantes_${tipoLibro}_${selectedPeriodo}.pdf`
    );
  };

  const handleExcelPreliminar = () => {
    runExport(
      'excel-preliminar',
      `${API_BASE_URL}/api/export/preliminar-excel`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ruc: currentClient.ruc, periodo: selectedPeriodo })
      },
      `Preliminar_${currentClient.ruc}_${selectedPeriodo}.xlsx`
    );
  };

  const exportBtnStyle = {
    display: 'flex', alignItems: 'center', gap: '0.4rem',
    padding: '0.45rem 0.8rem', fontSize: '0.78rem',
  };

  return (
    <div className="view-container animate-fade-in" style={{padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%'}}>
      {/* Top Actions */}
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <div>
          <h2 style={{fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-main)', margin: 0}}>Exportación y Cierre</h2>
          <p style={{color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.25rem'}}>Genera reportes finales y consolida la documentación.</p>
        </div>
        <div style={{display: 'flex', gap: '0.5rem', flexWrap: 'wrap', justifyContent: 'flex-end'}}>
          <button className="btn btn-outline" style={exportBtnStyle} onClick={() => handleConsolidarPdf('COMPRAS')} disabled={downloadingAction !== null}>
            {downloadingAction === 'pdf-compras' ? <Loader2 size={13} className="spin" /> : <File size={13} />} PDF Compras
          </button>
          <button className="btn btn-outline" style={exportBtnStyle} onClick={() => handleConsolidarPdf('VENTAS')} disabled={downloadingAction !== null}>
            {downloadingAction === 'pdf-ventas' ? <Loader2 size={13} className="spin" /> : <File size={13} />} PDF Ventas
          </button>
          <button className="btn btn-outline" style={exportBtnStyle} onClick={handleExcelPreliminar} disabled={downloadingAction !== null}>
            {downloadingAction === 'excel-preliminar' ? <Loader2 size={13} className="spin" /> : <Download size={13} />} Excel Preliminar
          </button>
        </div>
      </div>

      <div style={{display: 'flex', gap: '1.5rem', flex: 1, overflow: 'hidden'}}>
        {/* Table Section */}
        <div className="glass-panel data-panel" style={{flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden'}}>
          <div className="table-header-actions" style={{padding: '1rem', borderBottom: '1px solid rgba(226, 232, 240, 0.8)', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <div className="table-title" style={{display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: 'var(--text-main)'}}>
              <Database size={18} color="var(--accent-primary)" />
              Libro Unificado ({filteredData.length})
            </div>
            
            <div className="search-box" style={{width: '200px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', display: 'flex', alignItems: 'center', padding: '0.4rem 0.8rem'}}>
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
              <div style={{textAlign: 'center', padding: '3rem', color: 'var(--text-muted)'}}>Seleccione un cliente y periodo para ver el consolidado.</div>
            ) : filteredData.length === 0 ? (
              <div style={{textAlign: 'center', padding: '3rem', color: 'var(--text-muted)'}}>
                <FileText size={48} style={{opacity: 0.3, margin: '0 auto 1rem auto', display: 'block'}} />
                No hay datos en el libro unificado para este periodo.
              </div>
            ) : (
              <table style={{width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem'}}>
                <thead>
                  <tr style={{textAlign: 'left', borderBottom: '2px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)'}}>
                    <th style={{padding: '0.75rem 0.5rem'}}>Libro</th>
                    <th style={{padding: '0.75rem 0.5rem'}}>Comprobante</th>
                    <th style={{padding: '0.75rem 0.5rem'}}>Tercero (RUC/Nombre)</th>
                    <th style={{padding: '0.75rem 0.5rem', textAlign: 'right'}}>Total</th>
                    <th style={{padding: '0.75rem 0.5rem'}}></th>
                  </tr>
                </thead>
                <tbody>
                  {filteredData.map((row, i) => (
                    <tr 
                      key={i} 
                      onClick={() => setSelectedDoc(row)}
                      style={{
                        borderBottom: '1px solid rgba(255,255,255,0.06)',
                        cursor: 'pointer',
                        background: selectedDoc === row ? 'rgba(124, 58, 237, 0.1)' : 'transparent',
                        transition: 'background 0.2s'
                      }}
                      className="hover:bg-slate-50"
                    >
                      <td style={{padding: '0.75rem 0.5rem'}}>
                        <span className="badge" style={{
                          background: row.libro === 'COMPRAS' ? 'rgba(99,102,241,0.15)' : 'rgba(16,185,129,0.15)',
                          color: row.libro === 'COMPRAS' ? '#818cf8' : '#34d399'
                        }}>
                          {row.libro}
                        </span>
                      </td>
                      <td style={{padding: '0.75rem 0.5rem'}}>
                        <div style={{fontFamily: 'monospace', fontWeight: 600, color: 'var(--text-main)'}}>{row.serie_cdp}-{row.nro_cp}</div>
                        <div style={{fontSize: '0.75rem', color: 'var(--text-muted)'}}>{row.fecha_emision}</div>
                      </td>
                      <td style={{padding: '0.75rem 0.5rem'}}>
                        <div style={{fontWeight: 600, color: 'var(--text-main)'}}>{row.ruc_tercero}</div>
                        <div style={{fontSize: '0.75rem', color: 'var(--text-muted)', maxWidth: '200px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}} title={row.nombre_tercero}>
                          {row.nombre_tercero}
                        </div>
                      </td>
                      <td style={{padding: '0.75rem 0.5rem', textAlign: 'right', fontFamily: 'monospace', fontWeight: 600}}>
                        {Number(row.total_cp || 0).toFixed(2)}
                      </td>
                      <td style={{padding: '0.75rem 0.5rem', textAlign: 'right', color: 'var(--accent-primary)'}}>
                        <ChevronRight size={16} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Viewer Section */}
        <div className="glass-panel" style={{flex: '0 0 400px', display: 'flex', flexDirection: 'column', overflow: 'hidden'}}>
          <div style={{padding: '1rem', borderBottom: '1px solid rgba(226, 232, 240, 0.8)', display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: 'var(--text-main)'}}>
            <Eye size={18} color="var(--accent-primary)" />
            Visor de Documentos
          </div>
          
          <div style={{flex: 1, display: 'flex', flexDirection: 'column', background: 'rgba(255,255,255,0.015)', padding: '1.5rem', overflow: 'auto'}}>
            {!selectedDoc ? (
              <div style={{flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', textAlign: 'center', gap: '1rem'}}>
                <File size={48} style={{opacity: 0.3}} />
                <p>Selecciona un registro en la tabla para previsualizar el documento.</p>
              </div>
            ) : (
              <div style={{display: 'flex', flexDirection: 'column', gap: '1.5rem'}}>
                <div style={{background: 'rgba(255,255,255,0.04)', padding: '1.5rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)'}}>
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem', borderBottom: '1px dashed rgba(255,255,255,0.15)', paddingBottom: '1rem'}}>
                    <div>
                      <span className="badge" style={{background: selectedDoc.libro === 'COMPRAS' ? 'rgba(99,102,241,0.15)' : 'rgba(16,185,129,0.15)', color: selectedDoc.libro === 'COMPRAS' ? '#818cf8' : '#34d399', marginBottom: '0.5rem'}}>
                        {selectedDoc.libro}
                      </span>
                      <h3 style={{margin: '0.5rem 0 0 0', color: 'var(--text-main)', fontFamily: 'monospace', fontSize: '1.2rem'}}>{selectedDoc.serie_cdp}-{selectedDoc.nro_cp}</h3>
                    </div>
                    <div style={{textAlign: 'right'}}>
                      <div style={{fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase'}}>Total</div>
                      <div style={{fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-primary)'}}>S/ {Number(selectedDoc.total_cp || 0).toFixed(2)}</div>
                    </div>
                  </div>
                  
                  <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.85rem'}}>
                    <div>
                      <div style={{color: 'var(--text-muted)', marginBottom: '0.2rem'}}>Fecha Emisión</div>
                      <div style={{fontWeight: 600}}>{selectedDoc.fecha_emision}</div>
                    </div>
                    <div>
                      <div style={{color: 'var(--text-muted)', marginBottom: '0.2rem'}}>Moneda</div>
                      <div style={{fontWeight: 600}}>{selectedDoc.moneda || 'PEN'}</div>
                    </div>
                    <div style={{gridColumn: '1 / -1'}}>
                      <div style={{color: 'var(--text-muted)', marginBottom: '0.2rem'}}>{selectedDoc.libro === 'COMPRAS' ? 'Proveedor' : 'Cliente'}</div>
                      <div style={{fontWeight: 600}}>{selectedDoc.ruc_tercero}</div>
                      <div>{selectedDoc.nombre_tercero}</div>
                    </div>
                    <div style={{gridColumn: '1 / -1', marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px dashed rgba(255,255,255,0.15)', display: 'flex', justifyContent: 'space-between'}}>
                      <div>
                        <div style={{color: 'var(--text-muted)', marginBottom: '0.2rem'}}>Base Imponible</div>
                        <div style={{fontWeight: 600}}>S/ {Number(selectedDoc.base_imponible || 0).toFixed(2)}</div>
                      </div>
                      <div>
                        <div style={{color: 'var(--text-muted)', marginBottom: '0.2rem'}}>IGV</div>
                        <div style={{fontWeight: 600}}>S/ {Number(selectedDoc.igv || 0).toFixed(2)}</div>
                      </div>
                    </div>
                  </div>
                </div>

                <div style={{background: 'rgba(37, 99, 235, 0.05)', border: '1px dashed rgba(37, 99, 235, 0.3)', borderRadius: '12px', padding: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', color: 'var(--accent-primary)'}}>
                  <CheckCircle2 size={32} style={{opacity: 0.5}} />
                  <div style={{textAlign: 'center', fontSize: '0.85rem'}}>
                    <p style={{margin: '0 0 0.5rem 0', fontWeight: 600}}>Previsualización de Documento</p>
                    <p style={{margin: 0, opacity: 0.8}}>El archivo físico (PDF) se mostrará aquí cuando esté disponible.</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
