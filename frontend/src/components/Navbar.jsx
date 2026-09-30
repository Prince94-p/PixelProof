import React, { useState } from 'react';
import { ShieldCheck, Scan, Menu, X, ArrowRight, Layers, FileCheck } from 'lucide-react';

export default function Navbar({ currentPage, setCurrentPage }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { id: 'analyze', label: 'Analyze Image' },
    { id: 'how-it-works', label: 'How It Works' },
    { id: 'home', label: 'Forensic Lab' },
  ];

  const handleNavClick = (pageId) => {
    setCurrentPage(pageId);
    setMobileMenuOpen(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <header style={{
      backgroundColor: '#FFFFFF',
      borderBottom: '1px solid #E2E8F0',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      boxShadow: '0 1px 3px 0 rgba(15, 23, 42, 0.04)'
    }}>
      <div className="container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '70px',
      }}>
        {/* Left: PixelProof Brand Logo */}
        <div 
          onClick={() => handleNavClick('home')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            cursor: 'pointer',
            userSelect: 'none'
          }}
        >
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: '9px',
            backgroundColor: '#EFF6FF',
            border: '1.5px solid #DBEAFE',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#2563EB',
            boxShadow: '0 1px 2px rgba(37, 99, 235, 0.1)'
          }}>
            <Scan size={22} strokeWidth={2.4} />
          </div>
          <div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontWeight: 800,
              fontSize: '20px',
              letterSpacing: '-0.02em',
              color: '#0F172A'
            }}>
              Pixel<span style={{ color: '#2563EB' }}>Proof</span>
            </div>
            <div style={{
              fontSize: '11px',
              fontWeight: 600,
              color: '#64748B',
              letterSpacing: '0.04em',
              textTransform: 'uppercase',
              marginTop: '-2px'
            }}>
              Forensic Lab
            </div>
          </div>
        </div>

        {/* Center: Desktop Navigation */}
        <nav style={{
          display: 'none',
          alignItems: 'center',
          gap: '32px'
        }} className="desktop-nav">
          <button
            onClick={() => handleNavClick('analyze')}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '15px',
              fontWeight: currentPage === 'analyze' ? 700 : 500,
              color: currentPage === 'analyze' ? '#2563EB' : '#475569',
              cursor: 'pointer',
              padding: '6px 0',
              borderBottom: currentPage === 'analyze' ? '2px solid #2563EB' : '2px solid transparent',
              transition: 'all 0.15s ease'
            }}
          >
            Analyze
          </button>
          <button
            onClick={() => handleNavClick('how-it-works')}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '15px',
              fontWeight: currentPage === 'how-it-works' ? 700 : 500,
              color: currentPage === 'how-it-works' ? '#2563EB' : '#475569',
              cursor: 'pointer',
              padding: '6px 0',
              borderBottom: currentPage === 'how-it-works' ? '2px solid #2563EB' : '2px solid transparent',
              transition: 'all 0.15s ease'
            }}
          >
            How It Works
          </button>
          <button
            onClick={() => handleNavClick('home')}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '15px',
              fontWeight: currentPage === 'home' ? 700 : 500,
              color: currentPage === 'home' ? '#2563EB' : '#475569',
              cursor: 'pointer',
              padding: '6px 0',
              borderBottom: currentPage === 'home' ? '2px solid #2563EB' : '2px solid transparent',
              transition: 'all 0.15s ease'
            }}
          >
            Methodology
          </button>
        </nav>

        {/* Right: Primary Action Button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={() => handleNavClick('analyze')}
            className="btn-primary"
            style={{
              display: 'none',
            }}
            id="nav-analyze-btn"
          >
            <ShieldCheck size={17} />
            <span>Analyze Image</span>
          </button>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            style={{
              background: '#F1F5F9',
              border: '1px solid #E2E8F0',
              borderRadius: '8px',
              padding: '8px',
              color: '#0F172A',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            className="mobile-toggle"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div style={{
          backgroundColor: '#FFFFFF',
          borderBottom: '1px solid #E2E8F0',
          padding: '16px 24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
          boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)'
        }}>
          <button
            onClick={() => handleNavClick('analyze')}
            style={{
              textAlign: 'left',
              padding: '10px 14px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: currentPage === 'analyze' ? '#EFF6FF' : 'transparent',
              color: currentPage === 'analyze' ? '#2563EB' : '#0F172A',
              fontWeight: 600,
              fontSize: '15px',
              cursor: 'pointer'
            }}
          >
            Analyze Image
          </button>
          <button
            onClick={() => handleNavClick('how-it-works')}
            style={{
              textAlign: 'left',
              padding: '10px 14px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: currentPage === 'how-it-works' ? '#EFF6FF' : 'transparent',
              color: currentPage === 'how-it-works' ? '#2563EB' : '#0F172A',
              fontWeight: 600,
              fontSize: '15px',
              cursor: 'pointer'
            }}
          >
            How It Works
          </button>
          <button
            onClick={() => handleNavClick('home')}
            style={{
              textAlign: 'left',
              padding: '10px 14px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: currentPage === 'home' ? '#EFF6FF' : 'transparent',
              color: currentPage === 'home' ? '#2563EB' : '#0F172A',
              fontWeight: 600,
              fontSize: '15px',
              cursor: 'pointer'
            }}
          >
            Methodology & Overview
          </button>
        </div>
      )}

      {/* Media query styling inline */}
      <style>{`
        @media (min-width: 768px) {
          .desktop-nav {
            display: flex !important;
          }
          #nav-analyze-btn {
            display: inline-flex !important;
          }
          .mobile-toggle {
            display: none !important;
          }
        }
      `}</style>
    </header>
  );
}
