import React, { useState } from 'react';
import { FileText, Download, BarChart2 } from 'lucide-react';
import './Facturacion.css'; 

export default function ReportesView({ clientes, selectedCliente, onSelectCliente, addToast, apiBaseUrl }) {
  const [xmlFile, setXmlFile] = useState(null);
  const [periodo, setPeriodo] = useState('202401');
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerateReport = async () => {
    if (!selectedCliente) {
      addToast('Selecciona un cliente primero.', 'warning');
      return;
    }
    if (!periodo) {
      addToast('Ingresa un periodo válido (ej. 202401).', 'warning');
      return;
    }

    setIsGenerating(true);
    addToast('Generando reporte PDF (esto puede tomar unos segundos)...', 'info');
    try {
      const response = await fetch(`${apiBaseUrl}/api/pdf/report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cliente_id: selectedCliente, periodo: periodo })
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Reporte_Contable_${periodo}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        addToast('Reporte generado y descargado correctamente.', 'success');
      } else {
        const err = await response.json();
        addToast(`Error al generar el reporte: ${err.detail || 'Desconocido'}`, 'danger');
      }
    } catch (e) {
      addToast('Error de conexión con el servidor.', 'danger');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleGenerateInvoice = async () => {
    if (!xmlFile) {
      addToast('Selecciona un archivo XML primero.', 'warning');
      return;
    }

    setIsGenerating(true);
    addToast('Convirtiendo XML a PDF...', 'info');
    const formData = new FormData();
    formData.append('file', xmlFile);

    try {
      const response = await fetch(`${apiBaseUrl}/api/pdf/invoice`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Factura_${xmlFile.name}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        addToast('Factura generada y descargada correctamente.', 'success');
      } else {
        const err = await response.json();
        addToast(`Error al generar la factura: ${err.detail || 'Asegúrate de que es un XML válido UBL 2.1'}`, 'danger');
      }
    } catch (e) {
      addToast('Error de conexión con el servidor.', 'danger');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="facturacion-container animate-fade-in">
      <div className="facturacion-header">
        <div className="header-title">
          <BarChart2 size={24} color="#10b981" />
          <h2>Reportes Contables y PDFs</h2>
        </div>
        <p className="subtitle" style={{margin: 0}}>Generación de documentos estéticos en PDF para entrega a clientes finales</p>
      </div>

      <div className="facturacion-layout">
        <div className="form-column" style={{flex: 1, maxWidth: '600px', margin: '0 auto'}}>
          
          <div className="glass-panel form-section" style={{marginBottom: '2rem'}}>
            <h3 style={{borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '10px'}}><BarChart2 size={16} style={{display:'inline', verticalAlign:'text-bottom'}}/> 1. Reporte Financiero Mensual</h3>
            <p style={{fontSize: '0.85rem', color: '#94a3b8', marginBottom: '15px'}}>
              Genera un reporte gerencial estético en formato PDF con los totales de ventas, compras e IGV del periodo, listo para enviar al cliente.
            </p>
            <div className="control-group">
              <label>Cliente</label>
              <select value={selectedCliente} onChange={(e) => onSelectCliente(e.target.value)}>
                <option value="">-- Seleccionar Cliente --</option>
                {clientes.map(c => (
                  <option key={c.id} value={c.id}>{c.ruc} - {c.razon_social}</option>
                ))}
              </select>
            </div>
            <div className="control-group">
              <label>Periodo (YYYYMM)</label>
              <input type="text" value={periodo} onChange={e => setPeriodo(e.target.value)} placeholder="Ej: 202401" />
            </div>
            <button className="submit-btn" onClick={handleGenerateReport} disabled={isGenerating}>
              <Download size={18} /> {isGenerating ? 'Generando PDF...' : 'Descargar Reporte PDF'}
            </button>
          </div>

          <div className="glass-panel form-section">
            <h3 style={{borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '10px'}}><FileText size={16} style={{display:'inline', verticalAlign:'text-bottom'}}/> 2. Conversión Factura XML a PDF</h3>
            <p style={{fontSize: '0.85rem', color: '#94a3b8', marginBottom: '15px'}}>
              Sube un archivo XML de SUNAT (UBL 2.1) descargado del SIRE o facturador para generar su representación impresa profesional en formato PDF.
            </p>
            <div className="control-group">
              <input type="file" accept=".xml" onChange={(e) => setXmlFile(e.target.files[0])} style={{background: 'rgba(0,0,0,0.2)', padding: '10px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)'}} />
            </div>
            <button className="submit-btn" style={{background: '#3b82f6', borderColor: '#2563eb'}} onClick={handleGenerateInvoice} disabled={isGenerating || !xmlFile}>
              <FileText size={18} /> {isGenerating ? 'Generando PDF...' : 'Descargar Factura PDF'}
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}
