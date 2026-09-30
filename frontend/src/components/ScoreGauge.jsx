import React from 'react';
import { AlertTriangle, CheckCircle2, AlertOctagon, HelpCircle, Info } from 'lucide-react';

export default function ScoreGauge({ score, maxScore = 100, status, statusCode, confidence, confidenceDescription, summary, disclaimer }) {
  // Determine color and icon by status_code
  let themeColor = '#15803D'; // Green
  let themeBg = '#F0FDF4';
  let themeBorder = '#BBF7D0';
  let StatusIcon = CheckCircle2;

  if (statusCode === 'danger' || score >= 60) {
    themeColor = '#DC2626'; // Red
    themeBg = '#FEF2F2';
    themeBorder = '#FECACA';
    StatusIcon = AlertOctagon;
  } else if (statusCode === 'warning' || score >= 30) {
    themeColor = '#D97706'; // Amber
    themeBg = '#FFFBEB';
    themeBorder = '#FDE68A';
    StatusIcon = AlertTriangle;
  }

  // Calculate percentage position on horizontal meter
  const pct = Math.max(0, Math.min(100, (score / maxScore) * 100));

  return (
    <div className="card-white" style={{
      padding: '32px',
      border: '1px solid #E2E8F0',
      boxShadow: '0 2px 8px rgba(15, 23, 42, 0.04)',
      position: 'relative'
    }}>
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        gap: '24px',
        marginBottom: '28px'
      }}>
        {/* Left: Title & Main Score */}
        <div>
          <div style={{
            fontSize: '12px',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            color: '#64748B',
            marginBottom: '8px'
          }}>
            Overall Assessment
          </div>
          <h2 style={{
            fontSize: '22px',
            fontWeight: 800,
            color: '#0F172A',
            letterSpacing: '-0.02em',
            marginBottom: '4px'
          }}>
            Forensic Suspicion Score
          </h2>
          <div style={{
            display: 'flex',
            alignItems: 'baseline',
            gap: '8px',
            marginTop: '8px'
          }}>
            <span style={{
              fontSize: '56px',
              fontWeight: 800,
              lineHeight: 1,
              color: themeColor,
              letterSpacing: '-0.03em'
            }}>
              {score}
            </span>
            <span style={{
              fontSize: '22px',
              fontWeight: 600,
              color: '#94A3B8'
            }}>
              / {maxScore}
            </span>
          </div>
        </div>

        {/* Right: Status & Confidence Badges */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-start',
          gap: '12px'
        }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: themeBg,
            border: `1.5px solid ${themeBorder}`,
            color: themeColor,
            padding: '8px 16px',
            borderRadius: '10px',
            fontSize: '15px',
            fontWeight: 700,
            letterSpacing: '0.01em'
          }}>
            <StatusIcon size={20} strokeWidth={2.4} />
            <span>{status}</span>
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '13px',
            color: '#475569',
            backgroundColor: '#F8FAFC',
            border: '1px solid #E2E8F0',
            padding: '6px 12px',
            borderRadius: '8px'
          }}>
            <span style={{ fontWeight: 600, color: '#0F172A' }}>Confidence:</span>
            <span style={{
              fontWeight: 700,
              color: confidence === 'High' ? '#15803D' : (confidence === 'Moderate' ? '#2563EB' : '#D97706')
            }}>
              {confidence}
            </span>
            <span style={{ color: '#94A3B8' }}>•</span>
            <span style={{ color: '#64748B' }}>Initial evidence weights</span>
          </div>
        </div>
      </div>

      {/* Horizontal Evidence Meter */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '12px',
          fontWeight: 600,
          color: '#64748B',
          marginBottom: '8px'
        }}>
          <span style={{ color: '#15803D' }}>0–29 Low Suspicion</span>
          <span style={{ color: '#D97706' }}>30–59 Review Recommended</span>
          <span style={{ color: '#DC2626' }}>60–100 Strong Indicators</span>
        </div>

        {/* The Track with 3 colored bands */}
        <div style={{
          position: 'relative',
          height: '14px',
          borderRadius: '7px',
          overflow: 'visible',
          backgroundColor: '#E2E8F0',
          display: 'flex',
          boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.06)'
        }}>
          {/* Segment 1: Low (Green) */}
          <div style={{
            width: '30%',
            height: '100%',
            backgroundColor: '#86EFAC',
            borderTopLeftRadius: '7px',
            borderBottomLeftRadius: '7px',
            borderRight: '1px solid #FFFFFF'
          }} />
          {/* Segment 2: Review (Amber) */}
          <div style={{
            width: '30%',
            height: '100%',
            backgroundColor: '#FDE68A',
            borderRight: '1px solid #FFFFFF'
          }} />
          {/* Segment 3: Strong (Red) */}
          <div style={{
            width: '40%',
            height: '100%',
            backgroundColor: '#FECACA',
            borderTopRightRadius: '7px',
            borderBottomRightRadius: '7px'
          }} />

          {/* Indicator Needle Marker */}
          <div style={{
            position: 'absolute',
            left: `${pct}%`,
            top: '50%',
            transform: 'translate(-50%, -50%)',
            width: '24px',
            height: '24px',
            borderRadius: '50%',
            backgroundColor: '#FFFFFF',
            border: `3px solid ${themeColor}`,
            boxShadow: '0 2px 6px rgba(15, 23, 42, 0.25)',
            transition: 'left 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)',
            zIndex: 5
          }} />
        </div>
      </div>

      {/* Summary Box */}
      <div style={{
        backgroundColor: '#F8FAFC',
        border: '1px solid #E2E8F0',
        borderRadius: '10px',
        padding: '16px 20px',
        marginBottom: '16px'
      }}>
        <div style={{
          fontSize: '14px',
          fontWeight: 600,
          color: '#0F172A',
          marginBottom: '6px'
        }}>
          Forensic Summary:
        </div>
        <p style={{
          fontSize: '14px',
          lineHeight: '1.6',
          color: '#334155'
        }}>
          {summary}
        </p>
      </div>

      {/* Honest Scientific Disclaimer */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: '8px',
        fontSize: '12px',
        lineHeight: '1.5',
        color: '#64748B'
      }}>
        <Info size={15} style={{ flexShrink: 0, marginTop: '2px', color: '#2563EB' }} />
        <span>
          <strong>Scientific Principle:</strong> {disclaimer || "This score represents the strength of detected forensic indicators. It is not the probability that the image is fake."}
        </span>
      </div>
    </div>
  );
}
