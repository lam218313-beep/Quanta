import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Send, FileText, CheckCircle, AlertTriangle, Clock, ExternalLink } from 'lucide-react';
import './Facturacion.css';

export default function FacturacionView({ clientes, selectedCliente, onSelectCliente, addToast, apiBaseUrl }) {
  const [emisor, setEmisor] = useState(null);
  const [apiToken, setApiToken] = useState('');
  const [sandboxMode, setSandboxMode] = useState(true);
  
  useEffect(() => {
    if (selectedCliente) {
      const found = clientes.find(c => c.id === selectedCliente);
      setEmisor(found);
      // Si el cliente tiene token guardado, cargarlo
      if (found?.token_apisunat) setApiToken(found.token_apisunat);
    }
  }, [selectedCliente, clientes]);

  const [receptor, setReceptor] = useState({ ruc: '', razon_social: '', direccion: '' });
  const [comprobante, setComprobante] = useState({ 
    tipo: '01', 
    serie: 'F001', 
    correlativo: '', 
    fecha: new Date().toISOString().split('T')[0], 
    moneda: 'PEN' 
  });
  const [items, setItems] = useState([{ id: Date.now(), descripcion: '', cantidad: 1, precio_unitario: 0 }]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [emitResult, setEmitResult] = useState(null);

  const addItem = () => {
    setItems([...items, { id: Date.now(), descripcion: '', cantidad: 1, precio_unitario: 0 }]);
  };

  const removeItem = (id) => {
    if (items.length > 1) setItems(items.filter(item => item.id !== id));
  };

  const updateItem = (id, field, value) => {
    setItems(items.map(item => item.id === id ? { ...item, [field]: value } : item));
  };

  const subtotal = items.reduce((acc, item) => acc + (parseFloat(item.cantidad) || 0) * (parseFloat(item.precio_unitario) || 0), 0);
  const igv = subtotal * 0.18;
  const total = subtotal * 1.18;

  const handleEmitir = async () => {
    if (!emisor) { addToast('Selecciona un cliente Emisor primero.', 'warning'); return; }
    if (!apiToken.trim()) { addToast('Ingresa el token de APISUNAT para este cliente.', 'warning'); return; }
    if (!receptor.ruc || !receptor.razon_social) { addToast('Completa los datos del Receptor.', 'warning'); return; }
    const itemsValidos = items.filter(i => i.descripcion && parseFloat(i.precio_unitario) > 0);
    if (itemsValidos.length === 0) { addToast('Agrega al menos un ítem con descripción y precio.', 'warning'); return; }
    
    setIsSubmitting(true);
    setEmitResult(null);

    const payload = {
      emisor_ruc: emisor.ruc,
      receptor,
      comprobante,
      items: itemsValidos.map(i => ({
        descripcion: i.descripcion,
        cantidad: parseFloat(i.cantidad),
        precio_unitario: parseFloat(i.precio_unitario)
      })),
      totales: { subtotal, igv, total },
      token: apiToken,
      sandbox: sandboxMode
    };

    try {
      const response = await fetch(`${apiBaseUrl}/api/facturacion/emitir`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      
      if (response.ok) {
        addToast(`Comprobante ${data.estado || 'enviado'} correctamente.`, data.estado === 'ACEPTADO' ? 'success' : 'info');
        setEmitResult(data);
        setReceptor({ ruc: '', razon_social: '', direccion: '' });
        setItems([{ id: Date.now(), descripcion: '', cantidad: 1, precio_unitario: 0 }]);
      } else {
        addToast(`Error APISUNAT: ${data.detail || 'Error desconocido'}`, 'danger');
      }
    } catch (e) {
      addToast('Error de conexión al servidor.', 'danger');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getEstadoBadge = (estado) => {
    const map = {
      'ACEPTADO': { icon: <CheckCircle size={20} />, color: '#10b981', bg: 'rgba(16, 185, 129, 0.1)', border: 'rgba(16, 185, 129, 0.3)', text: 'Aceptado por SUNAT' },
      'PENDIENTE': { icon: <Clock size={20} />, color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)', border: 'rgba(245, 158, 11, 0.3)', text: 'Pendiente de procesamiento' },
      'RECHAZADO': { icon: <AlertTriangle size={20} />, color: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)', border: 'rgba(239, 68, 68, 0.3)', text: 'Rechazado por SUNAT' },
    };
    return map[estado] || map['PENDIENTE'];
  };

  return (
    <div className="facturacion-container animate-fade-in">
      <div className="facturacion-header">
        <div className="header-title">
          <FileText size={24} color="#7c3aed" />
          <h2>Emisión de Comprobantes Electrónicos</h2>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <p className="subtitle" style={{margin: 0}}>Integrado con APISUNAT → SUNAT</p>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', color: '#94a3b8', cursor: 'pointer' }}>
            <input 
              type="checkbox" 
              checked={sandboxMode} 
              onChange={e => setSandboxMode(e.target.checked)}
              style={{ accentColor: '#7c3aed', width: '16px', height: '16px' }}
            />
            Modo Sandbox (pruebas)
          </label>
        </div>
      </div>

      <div className="facturacion-layout">
        <div className="form-column">
          <div className="glass-panel form-section">
            <h3>1. Emisor (Tu Cliente)</h3>
            <div className="control-group">
              <label>Empresa Emisora</label>
              <select value={selectedCliente} onChange={(e) => onSelectCliente(e.target.value)}>
                <option value="">-- Seleccionar --</option>
                {clientes.map(c => (
                  <option key={c.id} value={c.id}>{c.ruc} - {c.razon_social}</option>
                ))}
              </select>
            </div>
            <div className="control-group">
              <label>
                Token APISUNAT 
                <a href="https://app.apisunat.pe" target="_blank" rel="noreferrer" style={{ marginLeft: '0.5rem', color: '#a78bfa', fontSize: '0.8rem' }}>
                  <ExternalLink size={12} style={{display:'inline'}} /> Obtener token
                </a>
              </label>
              <input 
                type="password" 
                value={apiToken} 
                onChange={e => setApiToken(e.target.value)} 
                placeholder="Bearer token de APISUNAT para esta empresa" 
              />
              <span style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem', display: 'block' }}>
                Único por empresa. Módulo "Organizaciones" en app.apisunat.pe
              </span>
            </div>
          </div>

          <div className="glass-panel form-section">
            <h3>2. Receptor (Tu Cliente Final)</h3>
            <div className="form-row">
              <div className="control-group">
                <label>RUC / DNI</label>
                <input type="text" value={receptor.ruc} onChange={e => setReceptor({...receptor, ruc: e.target.value})} placeholder="20123456789" />
              </div>
              <div className="control-group" style={{ flex: 2 }}>
                <label>Razón Social / Nombres</label>
                <input type="text" value={receptor.razon_social} onChange={e => setReceptor({...receptor, razon_social: e.target.value})} placeholder="Razón social del receptor" />
              </div>
            </div>
            <div className="control-group">
              <label>Dirección (Opcional)</label>
              <input type="text" value={receptor.direccion} onChange={e => setReceptor({...receptor, direccion: e.target.value})} placeholder="Av. Principal 123, Lima" />
            </div>
          </div>

          <div className="glass-panel form-section">
            <h3>3. Comprobante</h3>
            <div className="form-row">
              <div className="control-group">
                <label>Tipo</label>
                <select value={comprobante.tipo} onChange={e => {
                  const tipo = e.target.value;
                  setComprobante({...comprobante, tipo, serie: tipo === '01' ? 'F001' : 'B001'});
                }}>
                  <option value="01">Factura Electrónica</option>
                  <option value="03">Boleta de Venta</option>
                </select>
              </div>
              <div className="control-group">
                <label>Serie</label>
                <input type="text" value={comprobante.serie} onChange={e => setComprobante({...comprobante, serie: e.target.value.toUpperCase()})} />
              </div>
              <div className="control-group">
                <label>N° Correlativo</label>
                <input type="number" min="1" value={comprobante.correlativo} onChange={e => setComprobante({...comprobante, correlativo: e.target.value})} placeholder="1" />
              </div>
            </div>
            <div className="form-row">
              <div className="control-group">
                <label>Moneda</label>
                <select value={comprobante.moneda} onChange={e => setComprobante({...comprobante, moneda: e.target.value})}>
                  <option value="PEN">Soles (PEN)</option>
                  <option value="USD">Dólares (USD)</option>
                </select>
              </div>
              <div className="control-group">
                <label>Fecha de Emisión</label>
                <input type="date" value={comprobante.fecha} onChange={e => setComprobante({...comprobante, fecha: e.target.value})} />
              </div>
            </div>
          </div>
        </div>

        <div className="form-column">
          <div className="glass-panel form-section items-section">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{margin:0}}>4. Ítems</h3>
              <button className="btn-icon" onClick={addItem}><Plus size={18} /> Agregar</button>
            </div>
            
            <div className="items-list">
              {items.map((item, index) => (
                <div key={item.id} className="item-row animate-slide-up" style={{animationDelay: `${index * 0.05}s`}}>
                  <div className="control-group" style={{ flex: 3 }}>
                    <input type="text" placeholder="Descripción del producto/servicio" value={item.descripcion} onChange={e => updateItem(item.id, 'descripcion', e.target.value)} />
                  </div>
                  <div className="control-group" style={{ flex: 1, minWidth: '70px' }}>
                    <input type="number" placeholder="Cant." min="1" step="0.01" value={item.cantidad} onChange={e => updateItem(item.id, 'cantidad', e.target.value)} />
                  </div>
                  <div className="control-group" style={{ flex: 1.5, minWidth: '100px' }}>
                    <input type="number" placeholder="Precio c/IGV" step="0.01" value={item.precio_unitario} onChange={e => updateItem(item.id, 'precio_unitario', e.target.value)} />
                  </div>
                  <button className="btn-remove" onClick={() => removeItem(item.id)}><Trash2 size={16} /></button>
                </div>
              ))}
            </div>

            <div className="totales-card">
              <div className="total-row">
                <span>Op. Gravadas (sin IGV)</span>
                <span>{comprobante.moneda === 'PEN' ? 'S/ ' : '$ '}{subtotal.toFixed(2)}</span>
              </div>
              <div className="total-row">
                <span>IGV (18%)</span>
                <span>{comprobante.moneda === 'PEN' ? 'S/ ' : '$ '}{igv.toFixed(2)}</span>
              </div>
              <div className="total-row final-total">
                <span>Total a Pagar</span>
                <span>{comprobante.moneda === 'PEN' ? 'S/ ' : '$ '}{total.toFixed(2)}</span>
              </div>
            </div>

            {!emitResult ? (
              <button 
                className={`btn btn-primary btn-emitir ${isSubmitting ? 'loading' : ''}`}
                onClick={handleEmitir}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <span className="spinner"></span>
                ) : (
                  <><Send size={18} /> {sandboxMode ? 'Emitir (Sandbox)' : 'Emitir a SUNAT'}</>
                )}
              </button>
            ) : (
              <div className="emit-success-container animate-fade-in">
                {(() => {
                  const badge = getEstadoBadge(emitResult.estado);
                  return (
                    <div style={{ 
                      padding: '1.25rem', 
                      background: badge.bg, 
                      border: `1px solid ${badge.border}`, 
                      borderRadius: '10px', 
                      textAlign: 'center',
                      marginBottom: '0.75rem'
                    }}>
                      <div style={{ color: badge.color, marginBottom: '0.5rem' }}>{badge.icon}</div>
                      <h4 style={{ color: badge.color, margin: '0 0 0.25rem 0', fontSize: '1.1rem' }}>{badge.text}</h4>
                      {emitResult.message && <p style={{ color: '#94a3b8', fontSize: '0.85rem', margin: '0 0 1rem 0' }}>{emitResult.message}</p>}
                      
                      <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                        {emitResult.xml_url && (
                          <a href={emitResult.xml_url} target="_blank" rel="noreferrer" className="btn btn-secondary" style={{ flex: 1, minWidth: '130px', display: 'flex', justifyContent: 'center', gap: '0.4rem', background: 'rgba(255,255,255,0.05)' }}>
                            <FileText size={16} /> XML
                          </a>
                        )}
                        {emitResult.pdf_url && (
                          <a href={emitResult.pdf_url} target="_blank" rel="noreferrer" className="btn btn-secondary" style={{ flex: 1, minWidth: '130px', display: 'flex', justifyContent: 'center', gap: '0.4rem', background: 'rgba(255,255,255,0.05)' }}>
                            <FileText size={16} /> PDF
                          </a>
                        )}
                        {emitResult.cdr_url && (
                          <a href={emitResult.cdr_url} target="_blank" rel="noreferrer" className="btn btn-secondary" style={{ flex: 1, minWidth: '130px', display: 'flex', justifyContent: 'center', gap: '0.4rem', background: 'rgba(255,255,255,0.05)' }}>
                            <FileText size={16} /> CDR
                          </a>
                        )}
                      </div>
                    </div>
                  );
                })()}
                <button 
                  className="btn btn-primary"
                  style={{ width: '100%', background: 'transparent', border: '1px solid rgba(255,255,255,0.15)', color: '#e2e8f0' }}
                  onClick={() => setEmitResult(null)}
                >
                  <Plus size={16} /> Emitir Nuevo Comprobante
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
