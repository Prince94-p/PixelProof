import React from 'react';
import ScoreGauge from '../components/ScoreGauge';
import ForensicViewer from '../components/ForensicViewer';
import EvidenceCard from '../components/EvidenceCard';
import MetadataPanel from '../components/MetadataPanel';
import DigitalFingerprint from '../components/DigitalFingerprint';
import MLClassificationCard from '../components/MLClassificationCard';
import { ArrowLeft, RefreshCw, Download, FileText, CheckCircle2 } from 'lucide-react';

export default function Results({ analysisData, onReset }) {
  if (!analysisData) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 20px' }}>
        <h2>No analysis report available.</h2>
        <button onClick={onReset} className="btn-primary" style={{ marginTop: '16px' }}>
          Start an Analysis
        </button>
      </div>
    );
  }

  const { file, result, metadata, ela, copy_move, noise, file_integrity, evidence, original_preview, ml_analysis } = analysisData;
  const breakdown = result.breakdown || {};

  return (
    <div style={{
      backgroundColor: '#F7F9FC',
      minHeight: 'calc(100vh - 70px)',
      padding: '40px 0 80px 0'
    }}>
      <div className="container">
        {/* Report Top Header */}
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '16px',
          marginBottom: '28px'
        }}>
          <div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '12px',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              color: '#2563EB',
              marginBottom: '4px'
            }}>
              <span>EXPLAINABLE INVESTIGATIVE REPORT</span>
              <span style={{ color: '#94A3B8' }}>•</span>
              <span style={{ color: '#64748B', fontFamily: 'var(--font-mono)' }}>ID: {analysisData.analysis_id?.slice(0, 8)}</span>
            </div>

            <h1 style={{
              fontSize: '28px',
              fontWeight: 800,
              color: '#0F172A',
              letterSpacing: '-0.02em',
              marginBottom: '4px'
            }}>
              IMAGE FORENSIC REPORT
            </h1>

            <div style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '14px',
              fontSize: '13px',
              color: '#64748B'
            }}>
              <span>Target: <strong style={{ color: '#0F172A' }}>{file.filename}</strong></span>
              <span>•</span>
              <span>Timestamp: <strong style={{ color: '#0F172A' }}>{file.timestamp}</strong></span>
              <span>•</span>
              <span>Size: <strong style={{ color: '#0F172A' }}>{file.size_formatted}</strong></span>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={onReset}
              className="btn-secondary"
              style={{ padding: '10px 18px', fontSize: '14px' }}
            >
              <RefreshCw size={15} />
              <span>Analyze Another Image</span>
            </button>
          </div>
        </div>

        {/* 1. Overall Assessment Card (ScoreGauge) */}
        <div style={{ marginBottom: '32px' }}>
          <ScoreGauge
            score={result.score}
            maxScore={result.max_score}
            status={result.status}
            statusCode={result.status_code}
            confidence={result.confidence}
            confidenceDescription={result.confidence_description}
            summary={result.summary}
            disclaimer={result.disclaimer}
          />
        </div>

        {/* 2. Deep Learning ML Classification Signal (EfficientNet-B0) */}
        {ml_analysis?.available && (
          <MLClassificationCard
            mlAnalysis={ml_analysis}
            forensicScore={result?.score}
            forensicStatus={result?.status}
          />
        )}

        {/* 3. Visual Forensics Viewer */}
        <ForensicViewer
          originalImage={original_preview}
          ela={ela}
          copyMove={copy_move}
          noise={noise}
        />

        {/* 3. Evidence Breakdown: "WHY WAS THIS FLAGGED?" */}
        <div style={{ marginBottom: '36px' }}>
          <div style={{ marginBottom: '20px' }}>
            <div style={{
              fontSize: '12px',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              color: '#2563EB',
              marginBottom: '4px'
            }}>
              Inductive Findings
            </div>
            <h3 style={{
              fontSize: '22px',
              fontWeight: 800,
              color: '#0F172A',
              letterSpacing: '-0.02em'
            }}>
              WHY WAS THIS FLAGGED?
            </h3>
            <p style={{ fontSize: '14px', color: '#64748B', margin: 0 }}>
              Individual forensic modules evaluated independently against baseline image distributions:
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '20px'
          }}>
            {evidence && evidence.map((item) => (
              <EvidenceCard key={item.id} item={item} />
            ))}
          </div>
        </div>

        {/* 4. Score Breakdown Card */}
        <div className="card-white" style={{
          padding: '28px 32px',
          border: '1px solid #E2E8F0',
          marginBottom: '32px'
        }}>
          <h3 style={{
            fontSize: '18px',
            fontWeight: 800,
            color: '#0F172A',
            marginBottom: '20px'
          }}>
            FORENSIC SCORE BREAKDOWN
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Metadata Bar */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px', fontWeight: 600, marginBottom: '6px' }}>
                <span style={{ color: '#0F172A' }}>Metadata & Software Signatures</span>
                <span style={{ color: '#2563EB', fontFamily: 'var(--font-mono)' }}>
                  {breakdown.metadata?.score || 0} / {breakdown.metadata?.max || 15}
                </span>
              </div>
              <div style={{ height: '8px', backgroundColor: '#EFF6FF', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{
                  height: '100%',
                  backgroundColor: '#2563EB',
                  width: `${((breakdown.metadata?.score || 0) / (breakdown.metadata?.max || 15)) * 100}%`
                }} />
              </div>
            </div>

            {/* ELA Bar */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px', fontWeight: 600, marginBottom: '6px' }}>
                <span style={{ color: '#0F172A' }}>Error Level Analysis (90% Recompression)</span>
                <span style={{ color: '#2563EB', fontFamily: 'var(--font-mono)' }}>
                  {breakdown.ela?.score || 0} / {breakdown.ela?.max || 30}
                </span>
              </div>
              <div style={{ height: '8px', backgroundColor: '#EFF6FF', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{
                  height: '100%',
                  backgroundColor: '#2563EB',
                  width: `${((breakdown.ela?.score || 0) / (breakdown.ela?.max || 30)) * 100}%`
                }} />
              </div>
            </div>

            {/* Copy-Move Bar */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px', fontWeight: 600, marginBottom: '6px' }}>
                <span style={{ color: '#0F172A' }}>Copy-Move Duplicated Region Matching</span>
                <span style={{ color: '#2563EB', fontFamily: 'var(--font-mono)' }}>
                  {breakdown.copy_move?.score || 0} / {breakdown.copy_move?.max || 30}
                </span>
              </div>
              <div style={{ height: '8px', backgroundColor: '#EFF6FF', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{
                  height: '100%',
                  backgroundColor: '#2563EB',
                  width: `${((breakdown.copy_move?.score || 0) / (breakdown.copy_move?.max || 30)) * 100}%`
                }} />
              </div>
            </div>

            {/* Noise Bar */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px', fontWeight: 600, marginBottom: '6px' }}>
                <span style={{ color: '#0F172A' }}>High-Frequency Noise Residual Consistency</span>
                <span style={{ color: '#2563EB', fontFamily: 'var(--font-mono)' }}>
                  {breakdown.noise?.score || 0} / {breakdown.noise?.max || 20}
                </span>
              </div>
              <div style={{ height: '8px', backgroundColor: '#EFF6FF', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{
                  height: '100%',
                  backgroundColor: '#2563EB',
                  width: `${((breakdown.noise?.score || 0) / (breakdown.noise?.max || 20)) * 100}%`
                }} />
              </div>
            </div>

            {/* File Integrity Bar */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px', fontWeight: 600, marginBottom: '6px' }}>
                <span style={{ color: '#0F172A' }}>File Integrity & Container Markers</span>
                <span style={{ color: '#2563EB', fontFamily: 'var(--font-mono)' }}>
                  {breakdown.file_integrity?.score || 0} / {breakdown.file_integrity?.max || 5}
                </span>
              </div>
              <div style={{ height: '8px', backgroundColor: '#EFF6FF', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{
                  height: '100%',
                  backgroundColor: '#2563EB',
                  width: `${((breakdown.file_integrity?.score || 0) / (breakdown.file_integrity?.max || 5)) * 100}%`
                }} />
              </div>
            </div>

            {/* Total Row */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'baseline',
              paddingTop: '16px',
              borderTop: '1px solid #E2E8F0',
              marginTop: '8px'
            }}>
              <span style={{ fontSize: '15px', fontWeight: 800, color: '#0F172A' }}>TOTAL SUSPICION SCORE</span>
              <span style={{
                fontSize: '20px',
                fontWeight: 800,
                color: result.status_code === 'danger' ? '#DC2626' : (result.status_code === 'warning' ? '#D97706' : '#15803D'),
                fontFamily: 'var(--font-mono)'
              }}>
                {result.score} / 100
              </span>
            </div>
          </div>
        </div>

        {/* 5. Metadata Panel */}
        <MetadataPanel metadata={metadata} />

        {/* 6. Digital Fingerprint Card */}
        <DigitalFingerprint fileInfo={file} />
      </div>
    </div>
  );
}
