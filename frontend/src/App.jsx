import { useState } from "react";
import "./App.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function App() {
  const [username, setUsername] = useState("");
  const [roast, setRoast] = useState("");
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setRoast("");
    setProfile(null);

    if (!username.trim()) {
      setError("Please enter a GitHub username.");
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/roast`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.detail || "Failed to generate roast");
      }

      const data = await response.json();
      setRoast(data.roast || "");
      setProfile(data.profile || null);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1>GitHub Roaster</h1>

      <form onSubmit={handleSubmit} className="form">
        <label>
          GitHub username:
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="torvalds"
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "Roasting..." : "Roast me"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {profile && (
        <div className="profile">
          <h2>{profile.login}</h2>
          {profile.avatar_url && (
            <img
              src={profile.avatar_url}
              alt={profile.login}
              className="avatar"
            />
          )}
          {profile.bio && <p>{profile.bio}</p>}
          <p>Public repos: {profile.public_repos}</p>
          <p>Followers: {profile.followers}</p>
          <a href={profile.html_url} target="_blank" rel="noreferrer">
            View GitHub profile
          </a>
        </div>
      )}

      {roast && (
        <div className="roast">
          <h2>Roast</h2>
          <p>{roast}</p>
        </div>
      )}
    </div>
  );
}

export default App;
