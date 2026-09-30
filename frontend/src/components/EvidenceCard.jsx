import React from 'react';
import { ShieldAlert, ShieldCheck, AlertTriangle, CheckCircle2, Link2, Info } from 'lucide-react';

export default function EvidenceCard({ item }) {
  const { id, module, status, status_type, score, max_score, finding, explanation, corroborated } = item;

  // Determine theme styles based on status_type
  let badgeClass = 'badge-success';
  let scoreColor = '#15803D';
  let borderColor = '#E2E8F0';
  let IconComponent = CheckCircle2;

  if (status_type === 'danger') {
    badgeClass = 'badge-danger';
    scoreColor = '#DC2626';
    borderColor = '#FECACA';
    IconComponent = ShieldAlert;
  } else if (status_type === 'warning') {
    badgeClass = 'badge-warning';
    scoreColor = '#D97706';
    borderColor = '#FDE68A';
    IconComponent = AlertTriangle;
  } else if (status_type === 'neutral') {
    badgeClass = 'badge-neutral';
    scoreColor = '#64748B';
    borderColor = '#E2E8F0';
    IconComponent = Info;
  }

  const paddedId = String(id).padStart(2, '0');

  return (
    <div className="card-white" style={{
      padding: '24px',
      border: `1px solid ${borderColor}`,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      position: 'relative'
    }}>
      {/* Top Bar: Number, Module Name, Status Badge */}
      <div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '14px',
          gap: '12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{
              fontSize: '13px',
              fontWeight: 800,
              color: '#2563EB',
              backgroundColor: '#EFF6FF',
              padding: '2px 8px',
              borderRadius: '6px',
              fontFamily: 'var(--font-mono)'
            }}>
              {paddedId}
            </span>
            <span style={{
              fontSize: '12px',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              color: '#64748B'
            }}>
              {module}
            </span>
          </div>

          <span className={`badge ${badgeClass}`}>
            <IconComponent size={13} strokeWidth={2.4} />
            <span>{status}</span>
          </span>
        </div>

        {/* Primary Finding */}
        <h4 style={{
          fontSize: '16px',
          fontWeight: 700,
          color: '#0F172A',
          marginBottom: '8px',
          lineHeight: '1.4'
        }}>
          {finding}
        </h4>

        {/* Forensic Explanation */}
        <p style={{
          fontSize: '14px',
          lineHeight: '1.6',
          color: '#475569',
          marginBottom: '16px'
        }}>
          {explanation}
        </p>
      </div>

      {/* Bottom Bar: Cross-corroboration & Score Contribution */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingTop: '14px',
        borderTop: '1px solid #F1F5F9',
        fontSize: '13px'
      }}>
        <div>
          {corroborated ? (
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '11px',
              fontWeight: 600,
              color: '#0891B2',
              backgroundColor: '#ECFEFF',
              padding: '3px 8px',
              borderRadius: '4px',
              border: '1px solid #CFFAFE'
            }}>
              <Link2 size={12} />
              <span>Cross-Corroborated</span>
            </span>
          ) : (
            <span style={{ color: '#94A3B8', fontSize: '12px' }}>Independent Engine</span>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
          <span style={{ fontSize: '11px', textTransform: 'uppercase', color: '#64748B', fontWeight: 600 }}>Score Impact:</span>
          <span style={{
            fontSize: '15px',
            fontWeight: 800,
            color: scoreColor,
            fontFamily: 'var(--font-mono)'
          }}>
            {score}
          </span>
          <span style={{ fontSize: '13px', color: '#94A3B8', fontWeight: 500 }}>
            / {max_score}
          </span>
        </div>
      </div>
    </div>
  );
}
