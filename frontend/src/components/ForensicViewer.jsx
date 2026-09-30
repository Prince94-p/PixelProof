import React, { useState } from 'react';
import { Eye, Layers, Copy, Activity, ZoomIn, Info, CheckCircle2 } from 'lucide-react';

export default function ForensicViewer({ originalImage, ela, copyMove, noise }) {
  const [activeTab, setActiveTab] = useState('ela'); // 'ela', 'copy_move', 'noise', 'original'

  const tabs = [
    { id: 'ela', label: 'Error Level Analysis (ELA)', icon: Activity, data: ela },
    { id: 'copy_move', label: 'Copy-Move (Cloning)', icon: Copy, data: copyMove },
    { id: 'noise', label: 'Noise Consistency', icon: Layers, data: noise },
    { id: 'original', label: 'Original Image', icon: Eye, data: null },
  ];

  // Get active visualization image
  let activeVisualization = null;
  let activeDetails = null;

  if (activeTab === 'ela') {
    activeVisualization = ela?.visualization;
    activeDetails = ela;
  } else if (activeTab === 'copy_move') {
    activeVisualization = copyMove?.visualization;
    activeDetails = copyMove;
  } else if (activeTab === 'noise') {
    activeVisualization = noise?.visualization;
    activeDetails = noise;
  } else {
    activeVisualization = originalImage;
  }

  return (
    <div className="card-white" style={{
      padding: '32px',
      border: '1px solid #E2E8F0',
      boxShadow: '0 2px 8px rgba(15, 23, 42, 0.04)',
      marginBottom: '32px'
    }}>
      {/* Header and Title */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px',
        marginBottom: '24px'
      }}>
        <div>
          <div style={{
            fontSize: '12px',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            color: '#2563EB',
            marginBottom: '4px'
          }}>
            Comparative Evidence
          </div>
          <h3 style={{
            fontSize: '22px',
            fontWeight: 800,
            color: '#0F172A',
            letterSpacing: '-0.02em'
          }}>
            Visual Forensics
          </h3>
        </div>

        {/* Status indicator for selected engine */}
        {activeDetails && (
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '13px',
            fontWeight: 600,
            color: activeDetails.score >= (activeDetails.max_score * 0.6) ? '#DC2626' : (activeDetails.score > 0 ? '#D97706' : '#15803D'),
            backgroundColor: activeDetails.score >= (activeDetails.max_score * 0.6) ? '#FEF2F2' : (activeDetails.score > 0 ? '#FFFBEB' : '#F0FDF4'),
            border: `1px solid ${activeDetails.score >= (activeDetails.max_score * 0.6) ? '#FECACA' : (activeDetails.score > 0 ? '#FDE68A' : '#BBF7D0')}`,
            padding: '6px 14px',
            borderRadius: '9999px'
          }}>
            <span>Score: {activeDetails.score} / {activeDetails.max_score}</span>
            <span>•</span>
            <span>{activeDetails.status}</span>
          </div>
        )}
      </div>

      {/* Forensic Engine Tabs */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
        borderBottom: '1px solid #E2E8F0',
        paddingBottom: '16px',
        marginBottom: '24px'
      }}>
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '9px 18px',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: isActive ? 700 : 500,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                backgroundColor: isActive ? '#EFF6FF' : '#FFFFFF',
                color: isActive ? '#2563EB' : '#475569',
                border: isActive ? '1.5px solid #2563EB' : '1px solid #E2E8F0',
                boxShadow: isActive ? '0 1px 3px rgba(37, 99, 235, 0.12)' : 'none'
              }}
            >
              <Icon size={16} strokeWidth={isActive ? 2.4 : 2} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Dual Side-by-Side Visual Canvas */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '24px',
        marginBottom: '24px'
      }}>
        {/* Left Side: Original Image */}
        <div style={{
          backgroundColor: '#F8FAFC',
          border: '1px solid #E2E8F0',
          borderRadius: '10px',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <div style={{
            padding: '10px 16px',
            backgroundColor: '#FFFFFF',
            borderBottom: '1px solid #E2E8F0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '13px',
            fontWeight: 700,
            color: '#0F172A'
          }}>
            <span>ORIGINAL IMAGE (SOURCE)</span>
            <span style={{ fontSize: '11px', color: '#64748B', fontWeight: 500 }}>Reference Canvas</span>
          </div>
          <div style={{
            padding: '16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '360px',
            maxHeight: '480px',
            backgroundColor: '#F1F5F9'
          }}>
            {originalImage ? (
              <img
                src={originalImage}
                alt="Original uploaded source"
                style={{
                  maxWidth: '100%',
                  maxHeight: '440px',
                  objectFit: 'contain',
                  borderRadius: '6px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                }}
              />
            ) : (
              <div style={{ color: '#94A3B8', fontSize: '14px' }}>No image loaded</div>
            )}
          </div>
        </div>

        {/* Right Side: Forensic Scan Visualization */}
        <div style={{
          backgroundColor: '#F8FAFC',
          border: '1px solid #E2E8F0',
          borderRadius: '10px',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative'
        }}>
          <div style={{
            padding: '10px 16px',
            backgroundColor: '#FFFFFF',
            borderBottom: '1px solid #E2E8F0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '13px',
            fontWeight: 700,
            color: '#2563EB'
          }}>
            <span>
              {activeTab === 'ela' && 'ERROR LEVEL ANALYSIS (ELA RESIDUAL)'}
              {activeTab === 'copy_move' && 'ORB FEATURE CORRESPONDENCE & CLUSTERS'}
              {activeTab === 'noise' && 'LOCAL RESIDUAL NOISE VARIANCE HEATMAP'}
              {activeTab === 'original' && 'SOURCE INSPECTION'}
            </span>
            <span style={{
              fontSize: '11px',
              backgroundColor: '#EFF6FF',
              color: '#2563EB',
              border: '1px solid #DBEAFE',
              padding: '2px 8px',
              borderRadius: '4px',
              fontWeight: 600
            }}>
              Forensic Output
            </span>
          </div>

          <div style={{
            padding: '16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '360px',
            maxHeight: '480px',
            backgroundColor: '#F1F5F9',
            position: 'relative'
          }}>
            {activeVisualization ? (
              <img
                src={activeVisualization}
                alt="Forensic analysis overlay"
                style={{
                  maxWidth: '100%',
                  maxHeight: '440px',
                  objectFit: 'contain',
                  borderRadius: '6px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                }}
              />
            ) : (
              <div style={{ color: '#94A3B8', fontSize: '14px' }}>Visualization not available</div>
            )}
          </div>
        </div>
      </div>

      {/* Technical Interpretation Legend */}
      <div style={{
        backgroundColor: '#FFFFFF',
        border: '1px solid #E2E8F0',
        borderRadius: '10px',
        padding: '18px 22px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontWeight: 700,
          fontSize: '14px',
          color: '#0F172A',
          marginBottom: '8px'
        }}>
          <Info size={16} style={{ color: '#2563EB' }} />
          <span>Technical Interpretation Guide</span>
        </div>

        {activeTab === 'ela' && (
          <p style={{ fontSize: '13px', lineHeight: '1.6', color: '#475569' }}>
            <strong>How ELA works:</strong> The image is recompressed at a standardized 90% JPEG quality level. 
            Because each compression cycle introduces higher error in uncompressed or newly inserted pixels, 
            uniform areas should show consistent dull grain. Unusually bright or high-contrast patches against a uniform baseline 
            indicate divergent compression history (e.g. pasted or re-saved elements).
          </p>
        )}

        {activeTab === 'copy_move' && (
          <p style={{ fontSize: '13px', lineHeight: '1.6', color: '#475569' }}>
            <strong>How Copy-Move works:</strong> ORB (Oriented FAST and Rotated BRIEF) detects high-dimensional texture keypoints. 
            Points with matching descriptors that share a coherent spatial displacement vector are linked with blue lines. 
            Convex hulls highlight suspicious duplicate source/target areas. Note that natural repetitive textures (such as window grids, brick walls, or foliage) can produce benign false-positive matches.
          </p>
        )}

        {activeTab === 'noise' && (
          <p style={{ fontSize: '13px', lineHeight: '1.6', color: '#475569' }}>
            <strong>How Noise Consistency works:</strong> A high-pass filter extracts fine residual sensor noise grain. 
            The canvas is partitioned into blocks, and local noise dispersion (MAD) is computed. The false-color overlay 
            reveals localized deviations from the sensor noise floor—highlighting artificially smoothed areas or spliced objects from disparate camera sensors.
          </p>
        )}

        {activeTab === 'original' && (
          <p style={{ fontSize: '13px', lineHeight: '1.6', color: '#475569' }}>
            <strong>Source Reference:</strong> Displays the decoded input image in standard RGB color space. 
            Compare against the visual forensic tabs above to isolate suspicious features.
          </p>
        )}
      </div>
    </div>
  );
}
