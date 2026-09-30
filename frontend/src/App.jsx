import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import Analyze from './pages/Analyze';
import Results from './pages/Results';
import HowItWorks from './pages/HowItWorks';
import './styles.css';

export default function App() {
  const [currentPage, setCurrentPage] = useState('home'); // 'home' | 'analyze' | 'results' | 'how-it-works'
  const [analysisData, setAnalysisData] = useState(null);

  const handleAnalysisComplete = (data) => {
    setAnalysisData(data);
    setCurrentPage('results');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleResetAnalysis = () => {
    setAnalysisData(null);
    setCurrentPage('analyze');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      minHeight: '100vh',
      backgroundColor: '#F7F9FC'
    }}>
      {/* Strict Light Theme Navigation */}
      <Navbar currentPage={currentPage} setCurrentPage={setCurrentPage} />

      {/* Main Page Router */}
      <main style={{ flex: 1 }}>
        {currentPage === 'home' && (
          <Home setCurrentPage={setCurrentPage} />
        )}

        {currentPage === 'analyze' && (
          <Analyze onAnalysisComplete={handleAnalysisComplete} />
        )}

        {currentPage === 'results' && (
          <Results analysisData={analysisData} onReset={handleResetAnalysis} />
        )}

        {currentPage === 'how-it-works' && (
          <HowItWorks setCurrentPage={setCurrentPage} />
        )}
      </main>

      {/* Strict Light Theme Footer */}
      <Footer setCurrentPage={setCurrentPage} />
    </div>
  );
}
