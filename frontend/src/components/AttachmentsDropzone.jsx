import React, { useState, useEffect, useCallback } from 'react';
import { Upload, Trash2, FileText, Loader2 } from 'lucide-react';
import { supabase } from '../supabaseClient';

export default function AttachmentsDropzone({ clienteId, periodo, apiBaseUrl }) {
  const [attachments, setAttachments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState(null);

  const authHeader = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    return { Authorization: `Bearer ${session?.access_token}` };
  };

  const loadAttachments = useCallback(async () => {
    if (!clienteId || !periodo) return;
    setLoading(true);
    try {
      const headers = await authHeader();
      const res = await fetch(`${apiBaseUrl}/api/attachments/${clienteId}/${periodo}`, { headers });
      if (!res.ok) throw new Error('No se pudo cargar la lista de adjuntos');
      const data = await res.json();
      setAttachments(data.attachments || []);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [clienteId, periodo, apiBaseUrl]);

  useEffect(() => {
    loadAttachments();
  }, [loadAttachments]);

  const uploadFile = async (file) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Solo se aceptan archivos .pdf');
      return;
    }
    setUploading(true);
    setError(null);
    try {
      const headers = await authHeader();
      const formData = new FormData();
      formData.append('file', file);
      formData.append('cliente_id', clienteId);
      formData.append('periodo', periodo);
      const res = await fetch(`${apiBaseUrl}/api/attachments/upload`, {
        method: 'POST',
        headers,
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'No se pudo subir el archivo');
      }
      await loadAttachments();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) uploadFile(file);
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) uploadFile(file);
    e.target.value = '';
  };

  const handleDelete = async (id, nombre) => {
    if (!window.confirm(`¿Borrar "${nombre}"?`)) return;
    try {
      const headers = await authHeader();
      const res = await fetch(`${apiBaseUrl}/api/attachments/${id}`, { method: 'DELETE', headers });
      if (!res.ok) throw new Error('No se pudo borrar el adjunto');
      await loadAttachments();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
        Documentos adjuntos al informe
      </h3>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: 0 }}>
        NPS, constancias de declaración y otros PDFs que se agregarán al final del informe descargado para este período.
      </p>

      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        style={{
          border: `2px dashed ${dragOver ? 'var(--accent-primary)' : 'rgba(255,255,255,0.15)'}`,
          borderRadius: '8px',
          padding: '2rem',
          textAlign: 'center',
          color: 'var(--text-muted)',
          transition: 'border-color 0.2s',
        }}
      >
        {uploading ? (
          <Loader2 size={24} className="spin" style={{ marginBottom: '0.5rem' }} />
        ) : (
          <Upload size={24} style={{ marginBottom: '0.5rem', opacity: 0.6 }} />
        )}
        <p style={{ margin: '0 0 0.5rem 0' }}>
          {uploading ? 'Subiendo...' : 'Arrastra un PDF aquí, o'}
        </p>
        <label className="btn btn-outline" style={{ cursor: 'pointer', display: 'inline-flex' }}>
          Elegir archivo
          <input type="file" accept="application/pdf" onChange={handleFileSelect} style={{ display: 'none' }} disabled={uploading} />
        </label>
      </div>

      {error && <p style={{ color: '#ef4444', fontSize: '0.85rem', margin: 0 }}>{error}</p>}

      {loading ? (
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Cargando adjuntos...</p>
      ) : attachments.length === 0 ? (
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Sin adjuntos para este período.</p>
      ) : (
        <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {attachments.map((att) => (
            <li key={att.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 0.75rem', background: 'rgba(255,255,255,0.03)', borderRadius: '6px' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-main)', fontSize: '0.85rem' }}>
                <FileText size={16} />
                {att.nombre_archivo}
              </span>
              <button
                onClick={() => handleDelete(att.id, att.nombre_archivo)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#ef4444', display: 'flex', alignItems: 'center' }}
                title="Borrar"
              >
                <Trash2 size={16} />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
