import React, { useState, useEffect } from 'react';
import { Users, Search, Plus, Building2, CreditCard, CheckCircle2, AlertCircle, Clock, FileText, TrendingDown, ArrowLeft, Upload } from 'lucide-react';
import { supabase } from '../supabaseClient';

export default function ClientesView({ setActiveMainTab }) {
  const [clientes, setClientes] = useState([]);
  const [pagos, setPagos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('directorio'); // 'directorio' | 'pagos' | 'cliente'
  const [selectedCliente, setSelectedCliente] = useState(null);
  const [uploadingId, setUploadingId] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    const { data: clientesData, error: clientesError } = await supabase
      .from('clientes')
      .select('*')
      .order('razon_social', { ascending: true });
      
    if (clientesError) console.error('Error fetching clientes:', clientesError);
    else setClientes(clientesData || []);

    const { data: pagosData, error: pagosError } = await supabase
      .from('pagos_clientes')
      .select('*');

    if (pagosError) console.error('Error fetching pagos:', pagosError);
    else setPagos(pagosData || []);
    
    setLoading(false);
  };

  const getMesesPasados = () => {
    const meses = [];
    const date = new Date(); // Sept 2026 is current if OS time is 2026
    for(let i=0; i<6; i++){
      const monthNames = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
      meses.push(`${monthNames[date.getMonth()]} ${date.getFullYear()}`);
      date.setMonth(date.getMonth() - 1);
    }
    return meses;
  };

  const filteredClientes = clientes.filter(c => 
    (c.razon_social?.toLowerCase() || '').includes(searchTerm.toLowerCase()) || 
    (c.ruc || '').includes(searchTerm)
  );

  // Group payments by client to get the "current" state
  const getCurrentMes = () => getMesesPasados()[0];
  
  const pagosMap = pagos.reduce((acc, p) => {
    if (!acc[p.cliente_id]) acc[p.cliente_id] = [];
    acc[p.cliente_id].push(p);
    return acc;
  }, {});

  const currentPagosList = filteredClientes.map(c => {
    const clientPagos = pagosMap[c.id] || [];
    const currentMesStr = getCurrentMes();
    let currentPago = clientPagos.find(p => p.periodo === currentMesStr);
    
    return {
      cliente_id: c.id,
      cliente: c.razon_social,
      ruc: c.ruc,
      plan: 'Premium', // Can be fetched from DB if added
      monto: currentPago ? currentPago.monto : 150.00,
      estado: currentPago ? currentPago.estado : 'PENDIENTE',
      vencimiento: '30 ' + currentMesStr.split(' ')[0]
    };
  });

  const clientesActivos = clientes.filter(c => c.activo).length;
  const ingresosMensuales = currentPagosList.reduce((sum, p) => p.estado === 'PAGADO' ? sum + p.monto : sum, 0);
  const deudaAcumulada = currentPagosList.reduce((sum, p) => p.estado === 'PENDIENTE' ? sum + p.monto : sum, 0);
  const clientesDeudores = currentPagosList.filter(p => p.estado === 'PENDIENTE').length;

  const getBadgeStyle = (estado) => {
    if (estado === 'PAGADO') return { bg: 'rgba(16,185,129,0.15)', text: '#34d399', icon: <CheckCircle2 size={12} /> };
    if (estado === 'PENDIENTE') return { bg: 'rgba(239,68,68,0.15)', text: '#f87171', icon: <AlertCircle size={12} /> };
    return { bg: 'rgba(255,255,255,0.08)', text: '#94a3b8', icon: <Clock size={12} /> };
  };

  const handleVerCliente = async (clienteData) => {
    setSelectedCliente(clienteData);
    setActiveTab('cliente');

    // Auto-generate missing records for the last 6 months
    const meses = getMesesPasados();
    const existing = pagosMap[clienteData.cliente_id] || [];
    const missing = meses.filter(m => !existing.some(e => e.periodo === m));
    
    if (missing.length > 0) {
      const newRecords = missing.map(m => ({
        cliente_id: clienteData.cliente_id,
        periodo: m,
        monto: 150.00,
        estado: 'PENDIENTE'
      }));
      
      const { error } = await supabase.from('pagos_clientes').insert(newRecords);
      if (!error) {
        fetchData(); // reload
      } else {
        console.error('Error auto-generating payments', error);
      }
    }
  };

  const toggleEstadoPago = async (pagoId, currentEstado) => {
    const nuevoEstado = currentEstado === 'PENDIENTE' ? 'PAGADO' : 'PENDIENTE';
    const fechaPago = nuevoEstado === 'PAGADO' ? new Date().toISOString().split('T')[0] : null;

    // Optimistic UI update
    setPagos(prev => prev.map(p => p.id === pagoId ? { ...p, estado: nuevoEstado, fecha_pago: fechaPago } : p));
    
    const { error } = await supabase
      .from('pagos_clientes')
      .update({ estado: nuevoEstado, fecha_pago: fechaPago })
      .eq('id', pagoId);

    if (error) {
      console.error('Error toggling estado:', error);
      fetchData(); // rollback on error
    }
  };

  const handleFileUpload = async (event, pagoId) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadingId(pagoId);
    const fileExt = file.name.split('.').pop();
    const fileName = `${pagoId}_${Date.now()}.${fileExt}`;
    const filePath = `comprobantes/${fileName}`;

    try {
      const { error: uploadError } = await supabase.storage
        .from('comprobantes_pagos')
        .upload(filePath, file);

      if (uploadError) throw uploadError;

      const { data: publicData } = supabase.storage
        .from('comprobantes_pagos')
        .getPublicUrl(filePath);

      const publicUrl = publicData.publicUrl;

      // Update db
      await supabase.from('pagos_clientes').update({ ruta_comprobante: publicUrl }).eq('id', pagoId);
      
      // Local update
      setPagos(prev => prev.map(p => p.id === pagoId ? { ...p, ruta_comprobante: publicUrl } : p));

    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Error subiendo comprobante. Verifica que el bucket "comprobantes_pagos" exista.');
    } finally {
      setUploadingId(null);
    }
  };

  return (
    <div className="view-container animate-fade-in" style={{padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%'}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <div>
          <h2 style={{fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <Users size={24} color="var(--accent-primary)" />
            Mini CRM de Clientes
          </h2>
          <p style={{color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem'}}>Gestiona tus clientes activos, planes y su historial de facturación.</p>
        </div>
        <div style={{display: 'flex', gap: '1rem'}}>
          {activeTab === 'directorio' && (
            <button className="btn btn-primary" style={{display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'linear-gradient(135deg, #2563eb, #1d4ed8)'}}>
              <Plus size={16} /> Nuevo Cliente
            </button>
          )}
        </div>
      </div>

      <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem'}}>
        <div className="glass-panel" style={{padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem'}}>
          <div style={{color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <Building2 size={14} color="#3b82f6"/> Clientes Activos
          </div>
          <div style={{fontSize: '2rem', fontWeight: 700, color: 'var(--text-main)'}}>{clientesActivos}</div>
        </div>
        <div className="glass-panel" style={{padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem'}}>
          <div style={{color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <CreditCard size={14} color="#10b981"/> Ingresos Mensuales
          </div>
          <div style={{fontSize: '2rem', fontWeight: 700, color: 'var(--text-main)'}}>S/ {ingresosMensuales.toFixed(2)}</div>
        </div>
        <div className="glass-panel" style={{padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem'}}>
          <div style={{color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <TrendingDown size={14} color="#ef4444"/> Deuda Acumulada
          </div>
          <div style={{fontSize: '2rem', fontWeight: 700, color: '#ef4444'}}>S/ {deudaAcumulada.toFixed(2)}</div>
        </div>
        <div className="glass-panel" style={{padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem'}}>
          <div style={{color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <AlertCircle size={14} color="#ef4444"/> Clientes Deudores
          </div>
          <div style={{fontSize: '2rem', fontWeight: 700, color: '#ef4444'}}>{clientesDeudores}</div>
        </div>
      </div>

      <div style={{display: 'flex', gap: '1.5rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '0.5rem'}}>
        <button 
          onClick={() => setActiveTab('directorio')}
          style={{
            background: 'none', border: 'none', padding: '0.5rem 0', fontWeight: 600, cursor: 'pointer',
            color: activeTab === 'directorio' ? 'var(--accent-primary)' : 'var(--text-muted)',
            borderBottom: activeTab === 'directorio' ? '2px solid var(--accent-primary)' : '2px solid transparent',
            display: 'flex', alignItems: 'center', gap: '0.5rem'
          }}
        >
          <Building2 size={16} /> Directorio de Clientes
        </button>
        <button 
          onClick={() => setActiveTab('pagos')}
          style={{
            background: 'none', border: 'none', padding: '0.5rem 0', fontWeight: 600, cursor: 'pointer',
            color: activeTab === 'pagos' ? 'var(--accent-primary)' : 'var(--text-muted)',
            borderBottom: activeTab === 'pagos' ? '2px solid var(--accent-primary)' : '2px solid transparent',
            display: 'flex', alignItems: 'center', gap: '0.5rem'
          }}
        >
          <CreditCard size={16} /> Gestor de Pagos
        </button>
        {activeTab === 'cliente' && selectedCliente && (
          <button 
            style={{
              background: 'none', border: 'none', padding: '0.5rem 0', fontWeight: 600, cursor: 'default',
              color: 'var(--accent-primary)',
              borderBottom: '2px solid var(--accent-primary)',
              display: 'flex', alignItems: 'center', gap: '0.5rem'
            }}
          >
            <FileText size={16} /> Historial: {selectedCliente.cliente}
          </button>
        )}
      </div>

      <div className="glass-panel data-panel" style={{flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden'}}>
        {activeTab !== 'cliente' && (
          <div className="table-header-actions" style={{padding: '1rem', borderBottom: '1px solid rgba(226, 232, 240, 0.8)', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <div className="search-box" style={{width: '300px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', display: 'flex', alignItems: 'center', padding: '0.5rem 0.8rem'}}>
              <Search size={16} color="var(--text-muted)" style={{marginRight: '0.5rem'}} />
              <input 
                type="text" 
                placeholder="Buscar cliente o RUC..." 
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                style={{border: 'none', background: 'transparent', outline: 'none', fontSize: '0.9rem', color: 'var(--text-main)', width: '100%'}}
              />
            </div>
          </div>
        )}
        
        <div className="table-container" style={{flex: 1, overflow: 'auto', padding: activeTab === 'cliente' ? '0' : '1rem'}}>
          {loading ? (
            <div style={{textAlign: 'center', padding: '3rem', color: 'var(--text-muted)'}}>Cargando datos...</div>
          ) : activeTab === 'directorio' ? (
            <table style={{width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem'}}>
              <thead>
                <tr style={{textAlign: 'left', borderBottom: '2px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)'}}>
                  <th style={{padding: '0.75rem 0.5rem'}}>RUC</th>
                  <th style={{padding: '0.75rem 0.5rem'}}>Razón Social</th>
                  <th style={{padding: '0.75rem 0.5rem'}}>Rubro</th>
                  <th style={{padding: '0.75rem 0.5rem'}}>Usuario SOL</th>
                  <th style={{padding: '0.75rem 0.5rem', textAlign: 'center'}}>Estado</th>
                  <th style={{padding: '0.75rem 0.5rem', textAlign: 'center'}}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredClientes.map((cliente) => (
                  <tr key={cliente.id} style={{borderBottom: '1px solid rgba(255,255,255,0.06)'}} className="hover:bg-slate-50">
                    <td style={{padding: '0.75rem 0.5rem', fontFamily: 'monospace', fontWeight: 600}}>{cliente.ruc}</td>
                    <td style={{padding: '0.75rem 0.5rem', fontWeight: 600, color: 'var(--accent-primary)'}}>{cliente.razon_social}</td>
                    <td style={{padding: '0.75rem 0.5rem', color: 'var(--text-muted)', textTransform: 'capitalize'}}>{cliente.rubro || '-'}</td>
                    <td style={{padding: '0.75rem 0.5rem', fontFamily: 'monospace'}}>{cliente.usuario_sol}</td>
                    <td style={{padding: '0.75rem 0.5rem', textAlign: 'center'}}>
                      <span className="badge" style={{background: cliente.activo ? 'rgba(16,185,129,0.15)' : 'rgba(255,255,255,0.08)', color: cliente.activo ? '#34d399' : '#94a3b8'}}>
                        {cliente.activo ? 'ACTIVO' : 'INACTIVO'}
                      </span>
                    </td>
                    <td style={{padding: '0.75rem 0.5rem', textAlign: 'center'}}>
                      <button className="btn btn-outline" style={{padding: '0.3rem 0.6rem', fontSize: '0.75rem'}}>Editar</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : activeTab === 'pagos' ? (
            <table style={{width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem'}}>
              <thead>
                <tr style={{textAlign: 'left', borderBottom: '2px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)'}}>
                  <th style={{padding: '0.75rem 0.5rem'}}>Cliente</th>
                  <th style={{padding: '0.75rem 0.5rem'}}>Plan / Servicio</th>
                  <th style={{padding: '0.75rem 0.5rem', textAlign: 'right'}}>Monto Mensual</th>
                  <th style={{padding: '0.75rem 0.5rem'}}>Vencimiento</th>
                  <th style={{padding: '0.75rem 0.5rem', textAlign: 'center'}}>Estado Actual (Mes)</th>
                  <th style={{padding: '0.75rem 0.5rem', textAlign: 'center'}}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {currentPagosList.map((pago) => {
                  const style = getBadgeStyle(pago.estado);
                  return (
                    <tr 
                      key={pago.cliente_id} 
                      onClick={() => handleVerCliente(pago)}
                      style={{borderBottom: '1px solid rgba(255,255,255,0.06)', cursor: 'pointer'}}
                      className="hover:bg-slate-50"
                    >
                      <td style={{padding: '0.75rem 0.5rem'}}>
                        <div style={{fontWeight: 600, color: 'var(--text-main)'}}>{pago.cliente}</div>
                        <div style={{fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'monospace'}}>{pago.ruc}</div>
                      </td>
                      <td style={{padding: '0.75rem 0.5rem', color: 'var(--accent-primary)', fontWeight: 600}}>{pago.plan}</td>
                      <td style={{padding: '0.75rem 0.5rem', textAlign: 'right', fontWeight: 600, fontFamily: 'monospace'}}>
                        S/ {pago.monto.toFixed(2)}
                      </td>
                      <td style={{padding: '0.75rem 0.5rem'}}>{pago.vencimiento}</td>
                      <td style={{padding: '0.75rem 0.5rem', textAlign: 'center'}}>
                        <span className="badge" style={{background: style.bg, color: style.text, display: 'inline-flex', alignItems: 'center', gap: '0.25rem'}}>
                          {style.icon} {pago.estado}
                        </span>
                      </td>
                      <td style={{padding: '0.75rem 0.5rem', textAlign: 'center'}}>
                        <button className="btn btn-outline" style={{padding: '0.3rem 0.6rem', fontSize: '0.75rem'}} onClick={(e) => { e.stopPropagation(); }}>
                          Reporte
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          ) : (
            <div style={{display: 'flex', flexDirection: 'column', height: '100%'}}>
              <div style={{padding: '1.5rem', borderBottom: '1px solid rgba(255,255,255,0.1)', background: 'rgba(255,255,255,0.02)', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                <div>
                  <h3 style={{margin: '0 0 0.25rem 0', color: 'var(--text-main)', fontSize: '1.2rem'}}>{selectedCliente?.cliente}</h3>
                  <div style={{fontSize: '0.85rem', color: 'var(--text-muted)', fontFamily: 'monospace'}}>RUC: {selectedCliente?.ruc} • Plan: {selectedCliente?.plan} (S/ {selectedCliente?.monto.toFixed(2)})</div>
                </div>
                <button className="btn btn-outline" onClick={() => setActiveTab('pagos')} style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                  <ArrowLeft size={16} /> Volver a Pagos
                </button>
              </div>
              
              <div style={{padding: '1.5rem', flex: 1, overflow: 'auto'}}>
                <h4 style={{margin: '0 0 1rem 0', color: 'var(--text-main)'}}>Historial de Pagos (Últimos 6 meses)</h4>
                <table style={{width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem'}}>
                  <thead>
                    <tr style={{textAlign: 'left', borderBottom: '2px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)'}}>
                      <th style={{padding: '0.75rem 0.5rem'}}>Periodo</th>
                      <th style={{padding: '0.75rem 0.5rem', textAlign: 'right'}}>Monto Facturado</th>
                      <th style={{padding: '0.75rem 0.5rem', textAlign: 'center'}}>Estado</th>
                      <th style={{padding: '0.75rem 0.5rem', textAlign: 'center'}}>Fecha de Pago</th>
                      <th style={{padding: '0.75rem 0.5rem', textAlign: 'center'}}>Comprobante</th>
                    </tr>
                  </thead>
                  <tbody>
                    {getMesesPasados().map((mes, idx) => {
                      const pagoRec = (pagosMap[selectedCliente?.cliente_id] || []).find(p => p.periodo === mes);
                      if (!pagoRec) return null; // Shouldn't happen after auto-generate
                      
                      const style = getBadgeStyle(pagoRec.estado);

                      return (
                        <tr key={pagoRec.id} style={{borderBottom: '1px solid rgba(255,255,255,0.06)'}}>
                          <td style={{padding: '0.75rem 0.5rem', fontWeight: 600, color: 'var(--text-main)'}}>{mes}</td>
                          <td style={{padding: '0.75rem 0.5rem', textAlign: 'right', fontFamily: 'monospace'}}>S/ {pagoRec.monto.toFixed(2)}</td>
                          <td style={{padding: '0.75rem 0.5rem', textAlign: 'center'}}>
                            <button 
                              onClick={() => toggleEstadoPago(pagoRec.id, pagoRec.estado)}
                              className="badge" 
                              style={{background: style.bg, color: style.text, display: 'inline-flex', alignItems: 'center', gap: '0.25rem', border: '1px solid transparent', cursor: 'pointer', padding: '0.25rem 0.5rem', transition: 'all 0.2s', outline: 'none'}}
                              title="Clic para cambiar estado"
                            >
                              {style.icon} {pagoRec.estado}
                            </button>
                          </td>
                          <td style={{padding: '0.75rem 0.5rem', color: 'var(--text-muted)', textAlign: 'center'}}>{pagoRec.fecha_pago || '-'}</td>
                          <td style={{padding: '0.75rem 0.5rem', textAlign: 'center'}}>
                            {uploadingId === pagoRec.id ? (
                              <span style={{fontSize: '0.75rem', color: 'var(--text-muted)'}}>Subiendo...</span>
                            ) : pagoRec.ruta_comprobante ? (
                              <a href={pagoRec.ruta_comprobante} target="_blank" rel="noreferrer" className="btn btn-outline" style={{padding: '0.2rem 0.5rem', fontSize: '0.7rem', textDecoration: 'none'}}>
                                Ver PDF
                              </a>
                            ) : (
                              <label className="btn btn-outline" style={{padding: '0.2rem 0.5rem', fontSize: '0.7rem', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '0.25rem', margin: 0}}>
                                <Upload size={12} /> Subir
                                <input type="file" style={{display: 'none'}} accept=".pdf,image/*" onChange={(e) => handleFileUpload(e, pagoRec.id)} />
                              </label>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
