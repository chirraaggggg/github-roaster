import React, { useEffect, useRef } from 'react';
import '../styles/FloatingParticles.css';

const FloatingParticles = ({ count = 20 }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Clear existing particles
    container.innerHTML = '';

    // Create particles
    for (let i = 0; i < count; i++) {
      const particle = document.createElement('div');
      particle.className = 'particle';
      
      // Random size between 1px and 4px
      const size = Math.random() * 3 + 1;
      particle.style.width = `${size}px`;
      particle.style.height = `${size}px`;
      
      // Random position
      particle.style.left = `${Math.random() * 100}%`;
      particle.style.top = `${Math.random() * 100}%`;
      
      // Random animation duration between 10s and 30s
      const duration = Math.random() * 20 + 10;
      particle.style.animationDuration = `${duration}s`;
      
      // Random delay up to 10s
      particle.style.animationDelay = `-${Math.random() * 10}s`;
      
      container.appendChild(particle);
    }

    // Cleanup
    return () => {
      container.innerHTML = '';
    };
  }, [count]);

  return <div ref={containerRef} className="floating-particles" />;
};

export default FloatingParticles;
