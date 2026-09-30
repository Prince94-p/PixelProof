import React, { useState } from 'react';
import { Fingerprint, Copy, Check, Hash, FileCode, Clock, Shield } from 'lucide-react';

export default function DigitalFingerprint({ fileInfo }) {
  const [copied, setCopied] = useState(false);

  if (!fileInfo) return null;

  const handleCopyHash = () => {
    if (fileInfo.sha256) {
      navigator.clipboard.writeText(fileInfo.sha256);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  return (
    <div className="card-white" style={{
      padding: '28px',
      border: '1px solid #E2E8F0',
      marginBottom: '32px'
    }}>
      {/* Title */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '20px',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
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
            <Fingerprint size={20} strokeWidth={2.2} />
          </div>
          <div>
            <h3 style={{
              fontSize: '18px',
              fontWeight: 800,
              color: '#0F172A',
              marginBottom: '2px'
            }}>
              Digital Fingerprint & File Attributes
            </h3>
            <p style={{ fontSize: '13px', color: '#64748B', margin: 0 }}>
              Cryptographic integrity verification and container properties
            </p>
          </div>
        </div>

        <button
          onClick={handleCopyHash}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '7px 14px',
            borderRadius: '7px',
            backgroundColor: copied ? '#F0FDF4' : '#EFF6FF',
            color: copied ? '#15803D' : '#2563EB',
            border: `1px solid ${copied ? '#BBF7D0' : '#DBEAFE'}`,
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.15s ease'
          }}
        >
          {copied ? <Check size={14} /> : <Copy size={14} />}
          <span>{copied ? 'Hash Copied!' : 'Copy SHA-256'}</span>
        </button>
      </div>

      {/* SHA-256 Hash Display Box */}
      <div style={{
        backgroundColor: '#F8FAFC',
        border: '1px solid #E2E8F0',
        borderRadius: '8px',
        padding: '14px 18px',
        marginBottom: '20px'
      }}>
        <div style={{
          fontSize: '11px',
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.06em',
          color: '#64748B',
          marginBottom: '6px'
        }}>
          CRYPTOGRAPHIC SHA-256 HASH
        </div>
        <div style={{
          fontSize: '13px',
          fontFamily: 'var(--font-mono)',
          color: '#0F172A',
          wordBreak: 'break-all',
          lineHeight: '1.5',
          userSelect: 'all'
        }}>
          {fileInfo.sha256}
        </div>
      </div>

      {/* Technical File Attribute Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '12px',
        marginBottom: '18px'
      }}>
        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderRadius: '8px',
          padding: '12px 14px'
        }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: '#64748B', marginBottom: '2px' }}>FILENAME</div>
          <div style={{ fontSize: '13px', fontWeight: 700, color: '#0F172A', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {fileInfo.filename}
          </div>
        </div>

        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderRadius: '8px',
          padding: '12px 14px'
        }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: '#64748B', marginBottom: '2px' }}>FORMAT / MIME</div>
          <div style={{ fontSize: '13px', fontWeight: 700, color: '#0F172A' }}>
            {fileInfo.format} ({fileInfo.mime_type})
          </div>
        </div>

        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderRadius: '8px',
          padding: '12px 14px'
        }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: '#64748B', marginBottom: '2px' }}>DIMENSIONS</div>
          <div style={{ fontSize: '13px', fontWeight: 700, color: '#0F172A' }}>
            {fileInfo.width} × {fileInfo.height} px
          </div>
        </div>

        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderRadius: '8px',
          padding: '12px 14px'
        }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: '#64748B', marginBottom: '2px' }}>FILE SIZE</div>
          <div style={{ fontSize: '13px', fontWeight: 700, color: '#0F172A' }}>
            {fileInfo.size_formatted} ({fileInfo.size?.toLocaleString()} bytes)
          </div>
        </div>

        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderRadius: '8px',
          padding: '12px 14px'
        }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: '#64748B', marginBottom: '2px' }}>ANALYSIS TIME</div>
          <div style={{ fontSize: '13px', fontWeight: 600, color: '#0F172A', fontFamily: 'var(--font-mono)' }}>
            {fileInfo.timestamp}
          </div>
        </div>
      </div>

      {/* Explanation Notice */}
      <div style={{
        fontSize: '12px',
        color: '#64748B',
        lineHeight: '1.6',
        backgroundColor: '#F8FAFC',
        padding: '12px 16px',
        borderRadius: '8px',
        border: '1px solid #E2E8F0'
      }}>
        <strong>Forensic Principle:</strong> A SHA-256 hash provides an immutable digital fingerprint for this exact file byte-sequence. 
        Any modification—even altering a single pixel or metadata tag—produces a completely different hash. 
        <em> Note: Hashing verifies file integrity and provenance tracking; it does not detect manipulation on its own.</em>
      </div>
    </div>
  );
}
