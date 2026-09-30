import React from 'react';
import { 
  Activity, Copy, Layers, Camera, Fingerprint, 
  AlertTriangle, ShieldCheck, CheckCircle2, Info, ArrowRight, ArrowDown
} from 'lucide-react';

export default function HowItWorks({ setCurrentPage }) {
  return (
    <div style={{
      backgroundColor: '#FFFFFF',
      minHeight: 'calc(100vh - 70px)',
      padding: '56px 0 88px 0'
    }}>
      <div className="container">
        {/* Header */}
        <div style={{ textAlign: 'center', maxWidth: '780px', margin: '0 auto 60px auto' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: '#EFF6FF',
            color: '#2563EB',
            border: '1px solid #DBEAFE',
            padding: '6px 14px',
            borderRadius: '20px',
            fontSize: '12px',
            fontWeight: 700,
            letterSpacing: '0.06em',
            marginBottom: '16px'
          }}>
            <span>FORENSIC METHODOLOGY</span>
          </div>

          <h1 style={{
            fontSize: 'clamp(32px, 4.5vw, 48px)',
            fontWeight: 800,
            color: '#0F172A',
            letterSpacing: '-0.02em',
            marginBottom: '16px'
          }}>
            How PixelProof Verifies Authenticity
          </h1>
          <p style={{ fontSize: '17px', color: '#475569', lineHeight: '1.6' }}>
            PixelProof evaluates multiple independent physical, mathematical, and cryptographic properties of an image. 
            Here is the science behind each analysis module.
          </p>
        </div>

        {/* 5 Forensic Modules In-Depth */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '48px', marginBottom: '80px' }}>
          {/* Module 1: Metadata Forensics */}
          <div className="card-white" style={{ padding: '36px', border: '1px solid #E2E8F0', borderRadius: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '8px',
                backgroundColor: '#EFF6FF',
                color: '#2563EB',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Camera size={22} strokeWidth={2.4} />
              </div>
              <div>
                <span style={{ fontSize: '12px', fontWeight: 700, color: '#2563EB', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                  LAYER 01
                </span>
                <h3 style={{ fontSize: '22px', fontWeight: 800, color: '#0F172A' }}>
                  Metadata & EXIF Forensics
                </h3>
              </div>
            </div>

            <p style={{ fontSize: '15px', lineHeight: '1.6', color: '#475569', marginBottom: '20px' }}>
              When a camera records an image, it embeds hardware information (make, model, focal length, exposure time) into the Exchangeable Image File (EXIF) header. 
              Desktop and mobile photo editing applications (such as Adobe Photoshop, GIMP, Lightroom, Canva, and Snapseed) inject custom metadata tags during export.
            </p>

            <div style={{
              backgroundColor: '#F8FAFC',
              border: '1px solid #E2E8F0',
              borderRadius: '8px',
              padding: '16px 20px',
              marginBottom: '16px',
              fontFamily: 'var(--font-mono)',
              fontSize: '13px',
              lineHeight: '1.6',
              color: '#0F172A'
            }}>
              [RAW FILE BYTES] → [EXIF TAG DECODER] → [CAMERA SIGNATURE vs KNOWN EDITOR REGEX LIST]
            </div>

            <p style={{ fontSize: '14px', lineHeight: '1.6', color: '#64748B' }}>
              <strong>Key Principle:</strong> While presence of an editor string confirms post-processing, 
              the absence of EXIF metadata is completely normal when images are shared across platforms like WhatsApp, Twitter, or Instagram. 
              Therefore, missing metadata alone never increases the suspicion score.
            </p>
          </div>

          {/* Module 2: Error Level Analysis */}
          <div className="card-white" style={{ padding: '36px', border: '1px solid #E2E8F0', borderRadius: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '8px',
                backgroundColor: '#EFF6FF',
                color: '#2563EB',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Activity size={22} strokeWidth={2.4} />
              </div>
              <div>
                <span style={{ fontSize: '12px', fontWeight: 700, color: '#2563EB', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                  LAYER 02
                </span>
                <h3 style={{ fontSize: '22px', fontWeight: 800, color: '#0F172A' }}>
                  Error Level Analysis (ELA)
                </h3>
              </div>
            </div>

            <p style={{ fontSize: '15px', lineHeight: '1.6', color: '#475569', marginBottom: '20px' }}>
              JPEG is a lossy compression format operating on 8×8 discrete cosine transform (DCT) blocks. 
              Every time a JPEG is saved at a specific quality level (e.g. 90%), high-frequency details decay toward a steady-state error floor. 
              If an object is spliced from another image or retouched with brush tools, that region will have a different compression history.
            </p>

            <div style={{
              backgroundColor: '#F8FAFC',
              border: '1px solid #E2E8F0',
              borderRadius: '8px',
              padding: '16px 20px',
              marginBottom: '16px',
              fontFamily: 'var(--font-mono)',
              fontSize: '13px',
              lineHeight: '1.6',
              color: '#0F172A'
            }}>
              ORIGINAL(x,y) ──[Recompress at Q=90]──► RECOMPRESSED(x,y)<br />
              ERROR_MAP(x,y) = |ORIGINAL(x,y) - RECOMPRESSED(x,y)| × AMPLIFICATION_FACTOR
            </div>

            <p style={{ fontSize: '14px', lineHeight: '1.6', color: '#64748B' }}>
              <strong>Scientific Nuance:</strong> High-contrast natural edges naturally display slightly elevated recompression error. 
              PixelProof performs block-based variance analysis, searching for statistical outliers across non-edge patches rather than relying on global brightness.
            </p>
          </div>

          {/* Module 3: Copy-Move Forgery Detection */}
          <div className="card-white" style={{ padding: '36px', border: '1px solid #E2E8F0', borderRadius: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '8px',
                backgroundColor: '#EFF6FF',
                color: '#2563EB',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Copy size={22} strokeWidth={2.4} />
              </div>
              <div>
                <span style={{ fontSize: '12px', fontWeight: 700, color: '#2563EB', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                  LAYER 03
                </span>
                <h3 style={{ fontSize: '22px', fontWeight: 800, color: '#0F172A' }}>
                  Copy-Move (Cloning) Detection
                </h3>
              </div>
            </div>

            <p style={{ fontSize: '15px', lineHeight: '1.6', color: '#475569', marginBottom: '20px' }}>
              Copy-move tampering occurs when a region of the image is duplicated and pasted elsewhere (e.g. to cover an object, clone a crowd, or duplicate trees). 
              PixelProof detects this using OpenCV ORB (Oriented FAST and Rotated BRIEF) feature extraction, followed by nearest-neighbor descriptor matching within the same canvas.
            </p>

            <div style={{
              backgroundColor: '#F8FAFC',
              border: '1px solid #E2E8F0',
              borderRadius: '8px',
              padding: '16px 20px',
              marginBottom: '16px',
              fontFamily: 'var(--font-mono)',
              fontSize: '13px',
              lineHeight: '1.6',
              color: '#0F172A'
            }}>
              ORB KEYPOINTS → KNN MATCHING → DISTANCE FILTER (&gt;40px) → DISPLACEMENT VECTOR CLUSTERING (dx, dy)
            </div>

            <p style={{ fontSize: '14px', lineHeight: '1.6', color: '#64748B' }}>
              <strong>Safeguard Against False Positives:</strong> Repetitive natural textures (windows, brick patterns, grass blades) 
              share visual similarities but have randomized displacement vectors. 
              Genuine cloning produces mutually consistent translation vectors `(dx, dy)`. PixelProof requires coherent vector clusters before flagging suspicious regions.
            </p>
          </div>

          {/* Module 4: Local Noise Consistency Analysis */}
          <div className="card-white" style={{ padding: '36px', border: '1px solid #E2E8F0', borderRadius: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '8px',
                backgroundColor: '#EFF6FF',
                color: '#2563EB',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Layers size={22} strokeWidth={2.4} />
              </div>
              <div>
                <span style={{ fontSize: '12px', fontWeight: 700, color: '#2563EB', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                  LAYER 04
                </span>
                <h3 style={{ fontSize: '22px', fontWeight: 800, color: '#0F172A' }}>
                  Sensor Noise Consistency
                </h3>
              </div>
            </div>

            <p style={{ fontSize: '15px', lineHeight: '1.6', color: '#475569', marginBottom: '20px' }}>
              Digital camera sensors introduce subtle shot and read noise grain evenly across the sensor array. 
              When a foreign element is spliced in, or when a tool blurs a section of the skin or background, 
              the local noise variance deviates significantly from the image's global baseline.
            </p>

            <div style={{
              backgroundColor: '#F8FAFC',
              border: '1px solid #E2E8F0',
              borderRadius: '8px',
              padding: '16px 20px',
              marginBottom: '16px',
              fontFamily: 'var(--font-mono)',
              fontSize: '13px',
              lineHeight: '1.6',
              color: '#0F172A'
            }}>
              RESIDUAL = GRAY_IMAGE - GAUSSIAN_BLUR(GRAY_IMAGE)<br />
              LOCAL_NOISE_ESTIMATE = MEDIAN_ABSOLUTE_DEVIATION(RESIDUAL_BLOCK) / 0.6745
            </div>

            <p style={{ fontSize: '14px', lineHeight: '1.6', color: '#64748B' }}>
              <strong>Heatmap Generation:</strong> A false-color overlay maps the local noise standard deviation across 
              spatial grid blocks. Uniform noise produces a calm, balanced field; spliced regions stand out as stark discordant patches.
            </p>
          </div>

          {/* Module 5: Cryptographic Digital Fingerprint */}
          <div className="card-white" style={{ padding: '36px', border: '1px solid #E2E8F0', borderRadius: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '8px',
                backgroundColor: '#EFF6FF',
                color: '#2563EB',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Fingerprint size={22} strokeWidth={2.4} />
              </div>
              <div>
                <span style={{ fontSize: '12px', fontWeight: 700, color: '#2563EB', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                  LAYER 05
                </span>
                <h3 style={{ fontSize: '22px', fontWeight: 800, color: '#0F172A' }}>
                  Digital Fingerprint (SHA-256)
                </h3>
              </div>
            </div>

            <p style={{ fontSize: '15px', lineHeight: '1.6', color: '#475569', marginBottom: '20px' }}>
              PixelProof calculates the cryptographic SHA-256 hash of the exact binary payload uploaded. 
              Due to the cryptographic avalanche effect, changing even a single bit in the file produces a completely different hash string.
            </p>

            <p style={{ fontSize: '14px', lineHeight: '1.6', color: '#64748B' }}>
              <strong>Provenance Standard:</strong> The digital fingerprint allows investigators to establish chain-of-custody 
              and verify that an image introduced into evidence has not undergone any file mutation. 
              <em>Note: A hash verifies binary identity, not historical authenticity.</em>
            </p>
          </div>
        </div>

        {/* ============================================================
            CRITICAL SECTION: LIMITATIONS OF DIGITAL FORENSICS
            ============================================================ */}
        <div className="card-white" style={{
          padding: '40px',
          border: '1.5px solid #FDE68A',
          backgroundColor: '#FFFBEB',
          borderRadius: '16px',
          marginBottom: '60px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '18px' }}>
            <AlertTriangle size={26} style={{ color: '#D97706' }} />
            <h2 style={{ fontSize: '22px', fontWeight: 800, color: '#92400E' }}>
              LIMITATIONS OF DIGITAL IMAGE FORENSICS
            </h2>
          </div>

          <p style={{ fontSize: '15px', lineHeight: '1.6', color: '#78350F', marginBottom: '20px' }}>
            In forensic science, transparency requires clearly stating what a technique can and cannot determine. 
            PixelProof adheres strictly to evidentiary standards:
          </p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '16px',
            fontSize: '14px',
            lineHeight: '1.6',
            color: '#78350F'
          }}>
            <div style={{ backgroundColor: '#FFFFFF', padding: '16px', borderRadius: '8px', border: '1px solid #FDE68A' }}>
              <strong style={{ color: '#92400E' }}>Social Media Recompression:</strong> Platforms like WhatsApp, Twitter, and Facebook re-encode images through multiple aggressive compression passes, which can mask subtle ELA indicators or create artificial boundary artifacts.
            </div>

            <div style={{ backgroundColor: '#FFFFFF', padding: '16px', borderRadius: '8px', border: '1px solid #FDE68A' }}>
              <strong style={{ color: '#92400E' }}>Repeated Textures:</strong> Natural repetitive geometry (architectural windows, tile grids, repetitive foliage) can generate descriptor matches that mimic copy-move forgery.
            </div>

            <div style={{ backgroundColor: '#FFFFFF', padding: '16px', borderRadius: '8px', border: '1px solid #FDE68A' }}>
              <strong style={{ color: '#92400E' }}>Missing EXIF is Not Editing:</strong> Over 80% of images shared online have metadata stripped automatically by web servers. Absence of camera tags is an indicator of web transit, not forgery.
            </div>

            <div style={{ backgroundColor: '#FFFFFF', padding: '16px', borderRadius: '8px', border: '1px solid #FDE68A' }}>
              <strong style={{ color: '#92400E' }}>Depth-of-Field & Bokeh:</strong> Natural camera optical blur creates regions with low high-frequency noise that can appear anomalous without being tampered with.
            </div>
          </div>
        </div>

        {/* CTA */}
        <div style={{ textAlign: 'center' }}>
          <button
            onClick={() => { setCurrentPage('analyze'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
            className="btn-primary"
            style={{ padding: '14px 32px', fontSize: '16px' }}
          >
            <ShieldCheck size={20} />
            <span>Try Analysis on an Image</span>
          </button>
        </div>
      </div>
    </div>
  );
}
