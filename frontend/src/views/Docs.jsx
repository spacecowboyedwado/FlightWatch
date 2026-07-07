function Docs() {
    return (
        <main>
      <section className="page-header">
        <p className="label">API REFERENCE</p>
        <h1>Flight Watch API</h1>
        <p className="description">
          A small REST API for identifying aircraft from photo metadata. Send a photo
          or its EXIF data, get back the most likely flight in view.
        </p>
      </section>

      <div className="docs-layout">
        <nav className="docs-nav">
          <p className="card-label">ENDPOINTS</p>
          <a href="#match">POST /match</a>
          <a href="#flight">GET /flight/:id</a>
          <a href="#status">GET /status</a>
        </nav>

        <section className="docs-content">
          <article className="endpoint" id="match">
            <div className="endpoint-head">
              <span className="method">POST</span>
              <span className="endpoint-path">/match</span>
            </div>
            <div className="endpoint-body">
              <p>Upload a photo. Flight Watch extracts GPS coordinates and timestamp from EXIF data, then returns the closest matching aircraft from OpenSky Network data at that moment.</p>
              <div className="code-block">
                {`curl -X POST https://api.flightwatch.dev/match \\\n  -F "photo=@sunset.jpg"`}
              </div>
            </div>
          </article>

          <article className="endpoint" id="flight">
            <div className="endpoint-head">
              <span className="method">GET</span>
              <span className="endpoint-path">/flight/:id</span>
            </div>
            <div className="endpoint-body">
              <p>Look up details for a specific flight callsign returned from a previous match, including route, altitude, speed, and heading at the matched time.</p>
              <div className="code-block">curl https://api.flightwatch.dev/flight/ACA872</div>
            </div>
          </article>

          <article className="endpoint" id="status">
            <div className="endpoint-head">
              <span className="method">GET</span>
              <span className="endpoint-path">/status</span>
            </div>
            <div className="endpoint-body">
              <p>Check whether the OpenSky data feed is currently reachable. Useful before submitting a batch of photos.</p>
              <div className="code-block">curl https://api.flightwatch.dev/status</div>
            </div>
          </article>
        </section>
      </div>
    </main>
    );
}

export default Docs;