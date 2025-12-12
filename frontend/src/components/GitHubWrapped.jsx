const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

import React, { useState } from 'react';
import axios from 'axios';
import '../styles/GitHubWrapped.css';

const GitHubRoaster = () => {
  const [username, setUsername] = useState('');
  const [roast, setRoast] = useState('');
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // API base URL - points to the backend server
//   const API_BASE_URL = 'http://localhost:8000';  // or the correct URL

const handleSubmit = async (e) => {
  e.preventDefault();
  setError('');
  setRoast('');
  setProfile(null);
  
  if (!username.trim()) {
    setError('Please enter a GitHub username');
    return;
  }

  setLoading(true);
  try {
    console.log('Attempting to get roast for:', username);
    
    // Check if backend is reachable
    try {
      const healthCheck = await fetch(`${API_BASE_URL}/health`);
      if (!healthCheck.ok) {
        throw new Error('Backend health check failed');
      }
      console.log('Backend is reachable');
    } catch (healthErr) {
      console.error('Backend health check failed:', healthErr);
      throw new Error(`Cannot connect to backend at ${API_BASE_URL}. Is the server running?`);
    }

    // Make the roast request
    console.log('Requesting roast for:', username);
    const response = await fetch(`${API_BASE_URL}/roast`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify({ username }),
    });

    const data = await response.json().catch(() => ({}));
    
    if (!response.ok) {
      throw new Error(data?.detail || `Request failed with status ${response.status}`);
    }

    console.log('Roast response:', data);
    setRoast(data.roast || "");
    setProfile(data.profile || null);
    

  } catch (err) {
    const errorMessage = err.response?.data?.detail || 
                        err.message || 
                        'Failed to fetch data. Check console for details.';
    console.error('Error in handleSubmit:', {
      error: err,
      message: err.message,
      stack: err.stack,
    });
    setError(errorMessage);
  } finally {
    setLoading(false);
  }
};
  return (
    <div className="github-wrapped">
      {/* Background Pattern */}
      <div className="background-pattern"></div>
      
      {/* Main Content */}
      <div className="container">
        {/* Header */}
        <header className="header">
          <div className="version">v1.0</div>
          <h1>GITHUB ROASTER</h1>
          <p className="subtitle">YOUR CODE, ROASTED TO PERFECTION</p>
        </header>

        {/* Main Window */}
        <div className="app-window">
          <div className="window-header">
            <span>GITHUB_ROASTER.EXE</span>
            <span className="close-btn">x</span>
          </div>
          
          <div className="window-content">
            <form onSubmit={handleSubmit}>
              <div className="input-group">
                <label>&gt; Enter GitHub username</label>
                <div className="input-field">
                  <span>&gt;_</span>
                  <input 
                    type="text" 
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="octocat"
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="button-group">
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? 'ROASTING...' : 'GET ROASTED'}
                </button>
              </div>

              {error && <div className="error-message">{error}</div>}
            </form>

            {roast && (
              <div className="roast-output">
                <div className="roast-header">YOUR ROAST:</div>
                <div className="roast-text">{roast}</div>
              </div>
            )}

            {profile && (
              <div className="profile-info">
                <div className="profile-header">
                  <img 
                    src={profile.avatar_url} 
                    alt={profile.login}
                    className="profile-avatar"
                  />
                  <div>
                    <h3>{profile.name || profile.login}</h3>
                    <p>{profile.bio || 'No bio available'}</p>
                    <div className="profile-stats">
                      <span>Repos: {profile.public_repos}</span>
                      <span>Followers: {profile.followers}</span>
                      <span>Following: {profile.following}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Stats */}
        <div className="stats-container">
          <div className="stat">
            <div className="stat-number">1000+</div>
            <div className="stat-label">DEVS ROASTED</div>
          </div>
          <div className="stat">
            <div className="stat-number">99%</div>
            <div className="stat-label">EGO REDUCTION</div>
          </div>
          <div className="stat">
            <div className="stat-number">100%</div>
            <div className="stat-label">FUN GUARANTEED</div>
          </div>
        </div>

        {/* Footer */}
        <footer className="footer">
          <div className="built-by">
            built with ❤️ and a pinch of sarcasm
          </div>
          <div className="footer-links">
            <a href="#">ABOUT</a>
            <span className="divider">•</span>
            <a href="#">PRIVACY</a>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default GitHubRoaster;
