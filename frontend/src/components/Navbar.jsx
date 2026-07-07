// src/components/Navbar.jsx
import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

function Navbar() {
  const location = useLocation();
  // State to track if the hamburger menu is open or closed
  const [isOpen, setIsOpen] = useState(false);

  // Automatically close the menu whenever the route changes
  useEffect(() => {
    setIsOpen(false);
  }, [location]);

  return (
    <header className="nav">
      <Link className="logo" to="/">FLIGHT WATCH</Link>

      {/* The Hamburger Button */}
      <button
        className="menu-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle navigation"
      >
        {isOpen ? '✕' : '☰'} {/* Changes to an 'X' when open */}
      </button>

      {/* If isOpen is true, append the 'mobile-open' class */}
      <nav className={isOpen ? 'mobile-open' : ''}>
        <Link
          className={location.pathname === '/upload' ? 'active' : ''}
          to="/upload"
        >
          Upload
        </Link>

        <a href="/#how-it-works">How It Works</a>
        
        <Link 
          className={location.pathname === '/docs' ? 'active' : ''} 
          to="/docs"
        >
          API
        </Link>
        
        <a href="https://github.com" target="_blank" rel="noopener noreferrer">
          GitHub
        </a>
      </nav>
    </header>
  );
}

export default Navbar;