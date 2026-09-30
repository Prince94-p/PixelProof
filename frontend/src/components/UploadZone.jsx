import React, { useState, useRef } from 'react';
import { UploadCloud, Image as ImageIcon, X, FileCheck, ArrowRight, ShieldCheck, Sparkles } from 'lucide-react';

export default function UploadZone({ onAnalyze, isLoading }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [fileDetails, setFileDetails] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const fileInputRef = useRef(null);

  const handleFileProcess = (file) => {
    setErrorMsg('');
    if (!file) return;

    // Validate type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(jpg|jpeg|png|webp)$/i)) {
      setErrorMsg('Unsupported file format. Please upload a JPG, JPEG, PNG, or WEBP image.');
      return;
    }

    // Validate size (max 25MB)
    if (file.size > 25 * 1024 * 1024) {
      setErrorMsg('File size exceeds the 25 MB forensic limit.');
      return;
    }

    setSelectedFile(file);

    // Format readable size
    let sizeStr = `${file.size} bytes`;
    if (file.size > 1024 * 1024) {
      sizeStr = `${(file.size / (1024 * 1024)).toFixed(2)} MB`;
    } else if (file.size > 1024) {
      sizeStr = `${(file.size / 1024).toFixed(1)} KB`;
    }

    // Create object URL for client preview & read dimensions
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);

    const img = new Image();
    img.onload = () => {
      setFileDetails({
        name: file.name,
        size: sizeStr,
        width: img.naturalWidth,
        height: img.naturalHeight,
        type: file.type || 'image/jpeg'
      });
    };
    img.src = url;
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileProcess(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileProcess(e.target.files[0]);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    setFileDetails(null);
    setErrorMsg('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleSubmit = () => {
    if (selectedFile && !isLoading) {
      onAnalyze(selectedFile);
    }
  };

  // Helper to load synthetic demo samples directly from canvas
  const handleLoadSample = (sampleType) => {
    setErrorMsg('');
    const canvas = document.createElement('canvas');
    canvas.width = 720;
    canvas.height = 480;
    const ctx = canvas.getContext('2d');

    if (sampleType === 'clean') {
      // Natural landscape gradient with textured horizon
      const grad = ctx.createLinearGradient(0, 0, 0, 480);
      grad.addColorStop(0, '#7DD3FC');
      grad.addColorStop(0.5, '#E0F2FE');
      grad.addColorStop(0.8, '#86EFAC');
      grad.addColorStop(1, '#15803D');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 720, 480);

      // Natural mountain silhouettes
      ctx.fillStyle = '#1E3A8A';
      ctx.beginPath();
      ctx.moveTo(0, 360);
      ctx.lineTo(180, 220);
      ctx.lineTo(360, 340);
      ctx.lineTo(540, 200);
      ctx.lineTo(720, 360);
      ctx.lineTo(720, 480);
      ctx.lineTo(0, 480);
      ctx.closePath();
      ctx.fill();

      // Sun
      ctx.fillStyle = '#FDE047';
      ctx.beginPath();
      ctx.arc(360, 140, 40, 0, Math.PI * 2);
      ctx.fill();

      canvas.toBlob((blob) => {
        const file = new File([blob], 'natural_landscape_sample.jpg', { type: 'image/jpeg' });
        handleFileProcess(file);
      }, 'image/jpeg', 0.94);

    } else if (sampleType === 'cloned') {
      // Background with a deliberately duplicated stamped object
      ctx.fillStyle = '#F1F5F9';
      ctx.fillRect(0, 0, 720, 480);

      // Grid texture
      ctx.strokeStyle = '#CBD5E1';
      ctx.lineWidth = 1;
      for (let x = 0; x < 720; x += 40) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, 480);
        ctx.stroke();
      }

      // Source object (Textured emblem at 140, 200)
      const drawEmblem = (ox, oy) => {
        ctx.fillStyle = '#2563EB';
        ctx.fillRect(ox, oy, 110, 110);
        ctx.fillStyle = '#0891B2';
        ctx.beginPath();
        ctx.arc(ox + 55, oy + 55, 36, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#FFFFFF';
        ctx.font = 'bold 22px monospace';
        ctx.fillText('STAMP', ox + 22, oy + 62);
      };

      // Draw original
      drawEmblem(120, 180);
      // Cloned duplicate stamped in another zone (Copy-Move target)
      drawEmblem(460, 180);

      canvas.toBlob((blob) => {
        const file = new File([blob], 'controlled_copy_move_cloned.jpg', { type: 'image/jpeg' });
        handleFileProcess(file);
      }, 'image/jpeg', 0.92);

    } else if (sampleType === 'retouched') {
      // Image with a smooth airbrushed / low-noise patch in a textured field
      ctx.fillStyle = '#94A3B8';
      ctx.fillRect(0, 0, 720, 480);

      // Noise texture
      const imgData = ctx.getImageData(0, 0, 720, 480);
      const data = imgData.data;
      for (let i = 0; i < data.length; i += 4) {
        const n = (Math.random() - 0.5) * 55;
        data[i] = Math.min(255, Math.max(0, data[i] + n));
        data[i+1] = Math.min(255, Math.max(0, data[i+1] + n));
        data[i+2] = Math.min(255, Math.max(0, data[i+2] + n));
      }
      ctx.putImageData(imgData, 0, 0);

      // Artificial blur/smoothed spliced region (low noise anomaly)
      ctx.fillStyle = '#CBD5E1';
      ctx.beginPath();
      ctx.roundRect(240, 140, 240, 200, 16);
      ctx.fill();

      ctx.fillStyle = '#1D4ED8';
      ctx.font = 'bold 26px sans-serif';
      ctx.fillText('MODIFIED PATCH', 255, 248);

      canvas.toBlob((blob) => {
        const file = new File([blob], 'localized_ela_noise_anomaly.jpg', { type: 'image/jpeg' });
        handleFileProcess(file);
      }, 'image/jpeg', 0.88);
    }
  };

  return (
    <div style={{ maxWidth: '840px', margin: '0 auto' }}>
      {/* Upload Zone Card */}
      <div className="card-white" style={{
        padding: '36px',
        border: '1px solid #E2E8F0',
        boxShadow: '0 4px 12px rgba(15, 23, 42, 0.05)',
        marginBottom: '24px'
      }}>
        {/* Hidden File Input */}
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="image/jpeg,image/png,image/webp"
          style={{ display: 'none' }}
          id="forensic-file-input"
        />

        {!selectedFile ? (
          /* Empty State: Drag & Drop Container */
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            style={{
              border: `2px dashed ${isDragging ? '#2563EB' : '#93C5FD'}`,
              backgroundColor: isDragging ? '#EFF6FF' : '#F8FAFC',
              borderRadius: '12px',
              padding: '48px 24px',
              textAlign: 'center',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              outline: 'none'
            }}
          >
            <div style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              backgroundColor: '#EFF6FF',
              border: '1px solid #DBEAFE',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#2563EB',
              margin: '0 auto 20px auto'
            }}>
              <UploadCloud size={32} strokeWidth={2.2} />
            </div>

            <h3 style={{
              fontSize: '18px',
              fontWeight: 700,
              color: '#0F172A',
              marginBottom: '8px'
            }}>
              Drag & drop your image here
            </h3>
            <p style={{
              fontSize: '14px',
              color: '#64748B',
              marginBottom: '16px'
            }}>
              or <span style={{ color: '#2563EB', fontWeight: 600 }}>Browse Image</span> from your computer
            </p>

            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '12px',
              fontWeight: 600,
              color: '#64748B',
              backgroundColor: '#FFFFFF',
              border: '1px solid #E2E8F0',
              padding: '6px 14px',
              borderRadius: '20px'
            }}>
              <span>JPG</span>
              <span>•</span>
              <span>JPEG</span>
              <span>•</span>
              <span>PNG</span>
              <span>•</span>
              <span>WEBP</span>
              <span style={{ color: '#94A3B8' }}>(Up to 25 MB)</span>
            </div>
          </div>
        ) : (
          /* Selected State: Preview & Image Details */
          <div>
            <div style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '24px',
              alignItems: 'center',
              backgroundColor: '#F8FAFC',
              border: '1px solid #E2E8F0',
              borderRadius: '10px',
              padding: '20px',
              marginBottom: '24px'
            }}>
              {/* Preview Thumbnail */}
              <div style={{
                width: '120px',
                height: '120px',
                borderRadius: '8px',
                overflow: 'hidden',
                backgroundColor: '#FFFFFF',
                border: '1px solid #CBD5E1',
                flexShrink: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <img
                  src={previewUrl}
                  alt="Upload preview"
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'contain'
                  }}
                />
              </div>

              {/* File Info */}
              <div style={{ flex: 1, minWidth: '200px' }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '8px'
                }}>
                  <h4 style={{
                    fontSize: '16px',
                    fontWeight: 700,
                    color: '#0F172A',
                    wordBreak: 'break-all'
                  }}>
                    {fileDetails?.name || selectedFile.name}
                  </h4>
                  <button
                    onClick={handleClear}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#94A3B8',
                      cursor: 'pointer',
                      padding: '4px'
                    }}
                    title="Remove file"
                  >
                    <X size={18} />
                  </button>
                </div>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(110px, 1fr))',
                  gap: '8px',
                  fontSize: '13px'
                }}>
                  <div>
                    <span style={{ color: '#64748B' }}>Dimensions: </span>
                    <strong style={{ color: '#0F172A' }}>
                      {fileDetails?.width ? `${fileDetails.width} × ${fileDetails.height} px` : 'Detecting...'}
                    </strong>
                  </div>
                  <div>
                    <span style={{ color: '#64748B' }}>File Size: </span>
                    <strong style={{ color: '#0F172A' }}>{fileDetails?.size || ''}</strong>
                  </div>
                  <div>
                    <span style={{ color: '#64748B' }}>Format: </span>
                    <strong style={{ color: '#0F172A' }}>{selectedFile.type.replace('image/', '').toUpperCase()}</strong>
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap' }}>
              <button
                onClick={handleSubmit}
                disabled={isLoading}
                className="btn-primary"
                style={{
                  flex: 1,
                  minWidth: '220px',
                  padding: '14px 28px',
                  fontSize: '16px',
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  opacity: isLoading ? 0.7 : 1
                }}
                id="run-analysis-btn"
              >
                <ShieldCheck size={20} />
                <span>{isLoading ? 'ANALYZING...' : 'RUN FORENSIC ANALYSIS'}</span>
                {!isLoading && <ArrowRight size={18} />}
              </button>

              <button
                onClick={handleClear}
                disabled={isLoading}
                className="btn-secondary"
                style={{ padding: '14px 20px' }}
              >
                Change Image
              </button>
            </div>
          </div>
        )}

        {/* Error Message */}
        {errorMsg && (
          <div style={{
            marginTop: '16px',
            backgroundColor: '#FEF2F2',
            border: '1px solid #FECACA',
            color: '#DC2626',
            borderRadius: '8px',
            padding: '12px 16px',
            fontSize: '14px'
          }}>
            {errorMsg}
          </div>
        )}
      </div>

      {/* Preset Demo Samples Bar */}
      <div style={{
        backgroundColor: '#FFFFFF',
        border: '1px solid #E2E8F0',
        borderRadius: '12px',
        padding: '20px 24px',
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px'
      }}>
        <div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '13px',
            fontWeight: 700,
            color: '#0F172A',
            marginBottom: '2px'
          }}>
            <Sparkles size={15} style={{ color: '#0891B2' }} />
            <span>Try Instant Test Scenarios:</span>
          </div>
          <p style={{ fontSize: '13px', color: '#64748B', margin: 0 }}>
            No file on hand? Run verification on real synthetic test cases:
          </p>
        </div>

        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <button
            onClick={() => handleLoadSample('clean')}
            className="btn-outline-blue"
            style={{ fontSize: '12px', padding: '6px 12px' }}
          >
            Clean Photo
          </button>
          <button
            onClick={() => handleLoadSample('cloned')}
            className="btn-outline-blue"
            style={{ fontSize: '12px', padding: '6px 12px' }}
          >
            Cloned Stamp
          </button>
          <button
            onClick={() => handleLoadSample('retouched')}
            className="btn-outline-blue"
            style={{ fontSize: '12px', padding: '6px 12px' }}
          >
            Retouched Patch
          </button>
        </div>
      </div>
    </div>
  );
}
