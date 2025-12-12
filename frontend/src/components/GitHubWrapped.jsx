import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import '../styles/GitHubWrapped.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const formatJoinDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) return '';
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
};

const GitHubRoaster = () => {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [roast, setRoast] = useState('');
  const [profile, setProfile] = useState(null);
  const [modalType, setModalType] = useState('');
  const [navShift, setNavShift] = useState(0);
  const inputRef = useRef(null);
  const navigate = useNavigate();
  const { username: usernameParam } = useParams();
  const isRoastPage = Boolean(usernameParam);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [isRoastPage]);

  useEffect(() => {
    if (usernameParam) {
      setUsername(usernameParam);
    }
  }, [usernameParam]);

  // Clear roast data when returning to home page
  useEffect(() => {
    if (!isRoastPage) {
      setRoast('');
      setProfile(null);
      setError('');
      setLoading(false);
    }
  }, [isRoastPage]);

  useEffect(() => {
    const handleScroll = () => {
      const shift = Math.min(28, window.scrollY * 0.06);
      setNavShift(shift);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const body = document.body;
    const previous = body.style.overflow;
    if (isRoastPage) {
      body.style.overflow = 'hidden';
    } else {
      body.style.overflow = '';
    }
    return () => {
      body.style.overflow = previous;
    };
  }, [isRoastPage]);

  useEffect(() => {
    if (!isRoastPage || !usernameParam) {
      return;
    }

    const target = usernameParam.trim();
    if (!target) return;

    const controller = new AbortController();

    const fetchRoast = async () => {
      setLoading(true);
      setError('');
      setRoast('');
      setProfile(null);

      try {
        const response = await fetch(`${API_BASE_URL}/roast`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json'
          },
          body: JSON.stringify({ username: target }),
          signal: controller.signal
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
          throw new Error(data?.detail || `Request failed with status ${response.status}`);
        }

        setRoast(data.roast || '');
        setProfile(data.profile || null);
      } catch (err) {
        if (err?.name === 'AbortError') return;
        const message = err?.message || 'Failed to fetch data.';
        setError(message);
      } finally {
        setLoading(false);
      }
    };

    fetchRoast();
    return () => controller.abort();
  }, [isRoastPage, usernameParam]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = username.trim();
    setError('');

    if (!trimmed) {
      setError('Please enter a GitHub username.');
      return;
    }

    navigate(`/roast/${encodeURIComponent(trimmed)}`);
  };

  return (
    <div className="hero-screen">
      <div className="bg-grid" aria-hidden="true" />
      <div className="crt-overlay vignette" aria-hidden="true" />
      <div className="crt-overlay scanline" aria-hidden="true" />
      <div className="crt-overlay noise" aria-hidden="true" />

      <div className="content">
        <div className="version-chip">v1.0</div>
        <nav
          className="top-nav"
          aria-label="Main navigation"
          style={{ '--nav-shift': `${-navShift}px` }}
        >
          <a href="#home">home</a>
          <button type="button" onClick={() => setModalType('about')}>about</button>
          <button type="button" onClick={() => setModalType('privacy')}>privacy</button>
        </nav>

        {!isRoastPage && (
          <header className="hero" id="home">
            <h1 className="hero-title">GITHUB ROASTER</h1>
            <p className="hero-subtitle">Get Cooked (your commits)</p>
          </header>
        )}

        {!isRoastPage && (
          <>
            <section className="main-card">
              <div className="card-header">
                <span className="card-title">GIT_COOKED.EXE</span>
                <span className="card-close">✕</span>
              </div>

              <div className="card-body">
                <div className="label-line">&gt; Enter username</div>
                <form className="input-stack" onSubmit={handleSubmit}>
                  <input
                    ref={inputRef}
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    spellCheck="false"
                    autoComplete="off"
                    disabled={loading}
                    placeholder="octocat"
                    aria-label="GitHub username"
                  />
                  {error && <div className="error-line">{`> ${error}`}</div>}
                  <div className="button-row">
                    <button type="submit" className="btn primary" disabled={loading}>
                      {loading && isRoastPage ? 'ROASTING...' : 'GET ROASTED'}
                    </button>
                  </div>
                  <div className="helper-text">Press Enter to roast</div>
                </form>
              </div>
            </section>

            <section className="stats-row">
              <div className="stat">
                <div className="stat-number orange">100+</div>
                <div className="stat-label">DEVS ROASTED</div>
              </div>
              <div className="stat">
                <div className="stat-number cyan">99%</div>
                <div className="stat-label">EGO REDUCTION</div>
              </div>
              <div className="stat">
                <div className="stat-number magenta">100%</div>
                <div className="stat-label">FUN GUARANTEED</div>
              </div>
            </section>
          </>
        )}

        {(profile || roast) && (
          <section className="profile-roast">
            {profile && roast ? (
              <div className="profile-roast-card">
                <div className="profile-card">
                  <div className="avatar-wrap">
                    <img
                      className="avatar"
                      src={profile.avatar_url}
                      alt={profile.login}
                    />
                  </div>
                  <div className="profile-meta">
                    <div className="profile-name">{profile.name || profile.login}</div>
                    <div className="profile-username">@{profile.login}</div>
                    <div className="profile-stats-line">
                      <span>{profile.public_repos} repos</span>
                      <span>·</span>
                      <span>{profile.followers} followers</span>
                      <span>·</span>
                      <span>{profile.following} following</span>
                    </div>
                    {profile.bio && <div className="profile-bio">{profile.bio}</div>}
                    <div className="profile-extra">
                      {profile.location && (
                        <div className="info-chip">
                          <span className="chip-label">Location</span>
                          <span className="chip-value">{profile.location}</span>
                        </div>
                      )}
                      {profile.company && (
                        <div className="info-chip">
                          <span className="chip-label">Company</span>
                          <span className="chip-value">{profile.company}</span>
                        </div>
                      )}
                      {profile.blog && (
                        <div className="info-chip">
                          <span className="chip-label">Website</span>
                          <a className="chip-link" href={profile.blog.startsWith('http') ? profile.blog : `https://${profile.blog}`} target="_blank" rel="noreferrer">{profile.blog}</a>
                        </div>
                      )}
                      {profile.created_at && (
                        <div className="info-chip">
                          <span className="chip-label">Joined</span>
                          <span className="chip-value">{formatJoinDate(profile.created_at)}</span>
                        </div>
                      )}
                    </div>
                    <div className="profile-badges">
                      <span className="badge-pill">{profile.public_gists} gists</span>
                      <span className="badge-pill">{profile.public_repos} repos</span>
                      <span className="badge-pill">{profile.followers} fans</span>
                    </div>
                  </div>
                </div>
                <div className="roast-card">
                  <div className="roast-title">ROAST</div>
                  <div className="roast-body">{roast}</div>
                </div>
              </div>
            ) : (
              <>
                {profile && (
                  <div className="profile-panel">
                    <div className="avatar-wrap">
                      <img
                        className="avatar"
                        src={profile.avatar_url}
                        alt={profile.login}
                      />
                    </div>
                    <div className="profile-meta">
                      <div className="profile-name">{profile.name || profile.login}</div>
                      <div className="profile-username">@{profile.login}</div>
                      <div className="profile-stats-line">
                        <span>{profile.public_repos} repos</span>
                        <span>·</span>
                        <span>{profile.followers} followers</span>
                        <span>·</span>
                        <span>{profile.following} following</span>
                      </div>
                      {profile.bio && <div className="profile-bio">{profile.bio}</div>}
                      <div className="profile-extra">
                        {profile.location && (
                          <div className="info-chip">
                            <span className="chip-label">Location</span>
                            <span className="chip-value">{profile.location}</span>
                          </div>
                        )}
                        {profile.company && (
                          <div className="info-chip">
                            <span className="chip-label">Company</span>
                            <span className="chip-value">{profile.company}</span>
                          </div>
                        )}
                        {profile.blog && (
                          <div className="info-chip">
                            <span className="chip-label">Website</span>
                            <a className="chip-link" href={profile.blog.startsWith('http') ? profile.blog : `https://${profile.blog}`} target="_blank" rel="noreferrer">{profile.blog}</a>
                          </div>
                        )}
                        {profile.created_at && (
                          <div className="info-chip">
                            <span className="chip-label">Joined</span>
                            <span className="chip-value">{formatJoinDate(profile.created_at)}</span>
                          </div>
                        )}
                      </div>
                      <div className="profile-badges">
                        <span className="badge-pill">{profile.public_gists} gists</span>
                        <span className="badge-pill">{profile.public_repos} repos</span>
                        <span className="badge-pill">{profile.followers} fans</span>
                      </div>
                    </div>
                  </div>
                )}

                {roast && (
                  <div className="roast-panel">
                    <div className="roast-title">ROAST</div>
                    <div className="roast-body">{roast}</div>
                  </div>
                )}
              </>
            )}
          </section>
        )}

        {/* <div className="pill">built with 💋</div> */}

        <footer className="footer-links">
          <span className="footer-love">Built with ❤️</span>
          {isRoastPage && (
            <button className="btn primary" onClick={() => navigate('/')}>NEW ROAST</button>
          )}
        </footer>

        {modalType && (
          <div className="modal-overlay" role="dialog" aria-modal="true" aria-label={modalType === 'about' ? 'About' : 'Privacy'}>
            <div className={`modal-card ${modalType}`}>
              <div className="modal-header">
                <span className="modal-title">{modalType === 'about' ? 'ABOUT' : 'PRIVACY'}</span>
                <button className="modal-close" onClick={() => setModalType('')}>✕</button>
              </div>
              <div className="modal-body">
                {modalType === 'about' && (
                  <p>
                    Roasts are generated from your public GitHub footprint. We crunch commits, repos, and activity to serve a playful burn tailored to you.
                  </p>
                )}
                {modalType === 'privacy' && (
                  <p>
                    We only fetch the public GitHub data for the username you enter. Nothing is stored, logged, or shared. Close the tab, and the roast vanishes.
                  </p>
                )}
              </div>
              <button className="btn primary modal-cta" onClick={() => setModalType('')}>GOT IT</button>
            </div>
          </div>
        )}

        {loading && isRoastPage && (
          <div className="loading-overlay" role="status" aria-live="polite">
            <div className="loader" />
            <div className="loading-text">COOKING YOUR ROAST...</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GitHubRoaster;
