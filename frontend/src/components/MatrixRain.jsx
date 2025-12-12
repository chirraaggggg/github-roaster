import React, { useEffect, useRef } from 'react';
import '../styles/MatrixRain.css';

const MatrixRain = () => {
  const containerRef = useRef(null);
  const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
  
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    
    const fontSize = 16;
    const columns = Math.floor(window.innerWidth / fontSize);
    const rows = Math.floor(window.innerHeight / fontSize);
    
    // Create columns of characters
    for (let i = 0; i < columns; i++) {
      const column = document.createElement('div');
      column.className = 'matrix-column';
      column.style.left = `${i * fontSize}px`;
      column.style.animationDelay = `${Math.random() * 5}s`;
      column.style.animationDuration = `${5 + Math.random() * 10}s`;
      
      // Add characters to column
      for (let j = 0; j < rows; j++) {
        const char = document.createElement('span');
        char.textContent = chars[Math.floor(Math.random() * chars.length)];
        char.style.animationDelay = `${Math.random() * 5}s`;
        char.style.opacity = Math.random() * 0.5 + 0.1;
        column.appendChild(char);
      }
      
      container.appendChild(column);
    }
    
    // Cleanup function
    return () => {
      container.innerHTML = '';
    };
  }, []);
  
  return <div ref={containerRef} className="matrix-rain" />;
};

export default MatrixRain;
