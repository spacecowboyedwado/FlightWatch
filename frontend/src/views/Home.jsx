import {Link} from 'react-router-dom'

function Home() {
return (
    <main>
      <section className="hero">
        <div className="hero-text">
          <p className="label">AVIATION IMAGE INTELLIGENCE</p>
          <h1>Identify aircraft from the photos you already took.</h1>
          <p className="description">
            Flight Watch identifies aircraft from ordinary photos by combining EXIF GPS
            metadata, image timestamps, and OpenSky Network flight data.
          </p>
          <div className="buttons">
            <Link className="primary" to="/upload">
              Upload Image <span className="arrow">→</span>
            </Link>
            <Link className="secondary" to="/docs">
              View Documentation
            </Link>
          </div>
        </div>

        <div className="hero-preview">
          <div className="preview-header">
            <span className="preview-label">EXAMPLE RESULT</span>
            <span className="preview-status">96% MATCH</span>
          </div>
          <div className="flight-number">ACA872</div>
          <p className="flight-route">Toronto Pearson → London Heathrow</p>
          <div className="preview-grid">
            <div><span>Aircraft</span><strong>Boeing 787-9</strong></div>
            <div><span>Altitude</span><strong>34,012 ft</strong></div>
            <div><span>Ground Speed</span><strong>512 mph</strong></div>
            <div><span>Heading</span><strong>082°</strong></div>
          </div>
          <p className="preview-description">
            A sample aircraft report returned after Flight Watch compares photo
            metadata with nearby aircraft positions, heading, altitude, and time.
          </p>
        </div>
      </section>

      <section className="process" id="how-it-works">
        <div className="process-inner">
          <p className="label">How It Works</p>
          <h2>From photo to aircraft match.</h2>

          <div className="process-grid">
            <div className="process-card">
              <span>01</span>
              <div>
                <h3>Upload Photo</h3>
                <p>The backend extracts EXIF GPS and timestamp data from the image.</p>
              </div>
            </div>
            <div className="process-card">
              <span>02</span>
              <div>
                <h3>Scan Airspace</h3>
                <p>Flight Watch queries nearby aircraft from the OpenSky Network API.</p>
              </div>
            </div>
            <div className="process-card">
              <span>03</span>
              <div>
                <h3>Identify Aircraft</h3>
                <p>The system compares aircraft position, heading, altitude, and time.</p>
              </div>
            </div>
          </div>

          <Link to="/upload" className="button primary process-btn">
            Try It Now <span className="arrow">→</span>
          </Link>
        </div>
      </section>
    </main>
  );
}

export default Home;