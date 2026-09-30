import React, { useState } from 'react';
import { Camera, Calendar, Laptop, Navigation, Sparkles, ChevronDown, ChevronUp, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function MetadataPanel({ metadata }) {
  const [expanded, setExpanded] = useState(true);

  if (!metadata) return null;

  const details = metadata.details || {};
  const hasExif = details.has_exif;
  const isEditorDetected = Boolean(details.editor_detected);

  return (
    <div className="card-white" style={{
      border: '1px solid #E2E8F0',
      marginBottom: '32px',
      overflow: 'hidden'
    }}>
      {/* Header Bar */}
      <div 
        onClick={() => setExpanded(!expanded)}
        style={{
          padding: '20px 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
          backgroundColor: '#FFFFFF',
          userSelect: 'none',
          borderBottom: expanded ? '1px solid #E2E8F0' : 'none'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '8px',
            backgroundColor: '#EFF6FF',
            color: '#2563EB',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Camera size={20} strokeWidth={2.2} />
          </div>
          <div>
            <h3 style={{
              fontSize: '17px',
              fontWeight: 700,
              color: '#0F172A',
              marginBottom: '2px'
            }}>
              EXIF & Container Metadata
            </h3>
            <p style={{ fontSize: '13px', color: '#64748B', margin: 0 }}>
              Hardware tags, timestamps, software signatures, and capture headers
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className={`badge ${isEditorDetected ? 'badge-danger' : (hasExif ? 'badge-success' : 'badge-neutral')}`}>
            {isEditorDetected ? 'Editor Traces Found' : (hasExif ? 'EXIF Available' : 'EXIF Stripped')}
          </span>
          <button style={{
            background: 'none',
            border: 'none',
            color: '#64748B',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center'
          }}>
            {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
        </div>
      </div>

      {/* Expanded Content */}
      {expanded && (
        <div style={{ padding: '24px' }}>
          {/* Metadata Available Grid */}
          {hasExif ? (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '16px',
              marginBottom: '20px'
            }}>
              {/* Camera Model */}
              <div style={{
                backgroundColor: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '8px',
                padding: '14px 16px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#64748B', fontSize: '12px', fontWeight: 600, marginBottom: '6px' }}>
                  <Camera size={15} />
                  <span>CAMERA / HARDWARE</span>
                </div>
                <div style={{ fontSize: '15px', fontWeight: 700, color: '#0F172A' }}>
                  {details.camera || 'Not recorded'}
                </div>
              </div>

              {/* Software Signature */}
              <div style={{
                backgroundColor: isEditorDetected ? '#FEF2F2' : '#F8FAFC',
                border: `1px solid ${isEditorDetected ? '#FECACA' : '#E2E8F0'}`,
                borderRadius: '8px',
                padding: '14px 16px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: isEditorDetected ? '#DC2626' : '#64748B', fontSize: '12px', fontWeight: 600, marginBottom: '6px' }}>
                  <Laptop size={15} />
                  <span>SOFTWARE SIGNATURE</span>
                </div>
                <div style={{ fontSize: '15px', fontWeight: 700, color: isEditorDetected ? '#DC2626' : '#0F172A' }}>
                  {details.software || 'None detected'}
                </div>
              </div>

              {/* Timestamp */}
              <div style={{
                backgroundColor: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '8px',
                padding: '14px 16px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#64748B', fontSize: '12px', fontWeight: 600, marginBottom: '6px' }}>
                  <Calendar size={15} />
                  <span>ORIGINAL TIMESTAMP</span>
                </div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#0F172A', fontFamily: 'var(--font-mono)' }}>
                  {details.date_original !== 'Not recorded' ? details.date_original : (details.date_time || 'Not recorded')}
                </div>
              </div>

              {/* GPS Presence */}
              <div style={{
                backgroundColor: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '8px',
                padding: '14px 16px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#64748B', fontSize: '12px', fontWeight: 600, marginBottom: '6px' }}>
                  <Navigation size={15} />
                  <span>GEOLOCATION (GPS)</span>
                </div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#0F172A' }}>
                  {details.gps_recorded || 'Not recorded'}
                </div>
              </div>
            </div>
          ) : (
            /* Stripped Metadata Notice */
            <div style={{
              backgroundColor: '#F8FAFC',
              border: '1px solid #E2E8F0',
              borderRadius: '8px',
              padding: '20px',
              marginBottom: '20px',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '14px'
            }}>
              <AlertCircle size={22} style={{ color: '#0891B2', flexShrink: 0, marginTop: '2px' }} />
              <div>
                <h4 style={{ fontSize: '15px', fontWeight: 700, color: '#0F172A', marginBottom: '4px' }}>
                  METADATA UNAVAILABLE
                </h4>
                <p style={{ fontSize: '14px', lineHeight: '1.6', color: '#475569', margin: 0 }}>
                  Metadata may have been removed during normal image processing (such as messaging platforms, social media sharing, screenshots, or web CMS export). 
                  Its absence alone is not evidence of manipulation.
                </p>
              </div>
            </div>
          )}

          {/* Technical Note on EXIF Reliability */}
          <div style={{
            fontSize: '12px',
            color: '#64748B',
            lineHeight: '1.5',
            borderTop: '1px solid #F1F5F9',
            paddingTop: '14px'
          }}>
            <strong>Forensic Note:</strong> EXIF tags are easily stripped or spoofed by standard tools. 
            While detected editor traces (e.g. Adobe Photoshop, GIMP) confirm software handling, the absence of metadata is a normal consequence of web compression.
          </div>
        </div>
      )}
    </div>
  );
}
