import {useState} from 'react';
import axios from 'axios';
import exifr from "exifr";

function Upload() {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [flightData, setFlightData] = useState(null);
    const [error, setError] = useState(null);
    const [isDragOver, setIsDragOver] = useState(false);

    // Triggers whenever a file is dragged/dropped or browsed
    const handleFileChange = (selectedFile) => {
        if (selectedFile) {
            setFile(selectedFile);
            setError(null);
            // Immediately pass it to our API uploader function
            uploadToBackend(selectedFile);

        }
    };

    const uploadToBackend = async (fileToSend) => {
      setLoading(true);
      setFlightData(null);
      setError(null);

      const formData = new FormData();
      formData.append('file', fileToSend);


      try {
          const fullExif = await exifr.parse(fileToSend);
          
          if (fullExif) {
              formData.append('exif_data', JSON.stringify(fullExif));
              console.log("Client-side EXIF extracted: ", fullExif)
          } else {
              console.warn("No metadata found in this file copy.");
          }

          const response = await axios.post('/api/images/upload', formData, {
              headers: { 'Content-Type': 'multipart/form-data' },
          });

        setFlightData(response.data);
      } catch (err) {
        console.error(err);

        // Check if the server responded with a structured error message
        if (err.response && err.response.data && err.response.data.detail) {
          // Captures custom FastAPI messages
          setError(err.response.data.detail);
        } else {
          setError('Could not connect to the flight tracking service. Please try again later.');
        }
      } finally {
        setLoading(false);
      }
    };
    return (
    <main>
      <section className="page-header">
        <p className="label">UPLOAD A PHOTO</p>
        <h1>Find the aircraft in your photo.</h1>
        <p className="description">
          Choose a photo taken outdoors with GPS location enabled. Flight Watch reads
          the EXIF data and checks it against nearby flights at the moment the photo was taken.
        </p>
      </section>

      <section className="upload-wrap">
        {/* Interactive Drag & Drop Box */}
        <label
          className={`dropzone ${isDragOver ? 'dragover' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setIsDragOver(false);
            if (e.dataTransfer.files.length) handleFileChange(e.dataTransfer.files[0]);
          }}
          htmlFor="file-input"
        >
          <p className="dz-title">
            {file ? file.name : 'Drag a photo here'}
          </p>
          <p className="dz-sub">JPEG or HEIC, with location data enabled</p>
          <span className="dz-browse">or browse files</span>
          <input
            type="file"
            id="file-input"
            accept="image/*"
            hidden
            onChange={(e) => handleFileChange(e.target.files[0])}
          />
        </label>

        {/* Dynamic Context States Panel */}
        <div className="state-panel">
          {/* State A: Loading spinner layout while waiting for FastAPI */}
          {loading && (
            <div className="state-loading">
              <p className="dz-title">Processing Metadata...</p>
              <p>Extracting EXIF coordinates and scanning OpenSky airspace records.</p>
            </div>
          )}

          {/* State B: Error catch panel */}
          {error && (
            <div className="state-error" style={{ color: '#ff6b6b' }}>
              <p className="dz-title">Error</p>
              <p>{error}</p>
            </div>
          )}

          {/* State C: Idle layout before a user feeds a photo */}
          {!loading && !flightData && !error && (
            <div className="state-idle">
              <p className="dz-title">Waiting for a photo</p>
              <p>Once you add a photo, this panel will show progress, then the matched flight.</p>
            </div>
          )}

          {/* State D: Render the actual flight card matched from your Python algorithm */}
          {flightData && (
            <div className="hero-preview" style={{ margin: 0, width: '100%' }}>
              <div className="preview-header">
                <span className="preview-label">LIVE MATCH RESULT</span>
                <span className="preview-status">{flightData.match_confidence || '100%'} MATCH</span>
              </div>
              <div className="flight-number">{flightData.callsign || 'UNKNOWN'}</div>
              <p className="flight-route">{flightData.route || 'Route Data Unavailable'}</p>
              <div className="preview-grid">
                <div><span>Aircraft</span><strong>{flightData.aircraft_model || 'N/A'}</strong></div>
                <div><span>Altitude</span><strong>{flightData.altitude ? `${flightData.altitude} ft` : 'N/A'}</strong></div>
                <div><span>Ground Speed</span><strong>{flightData.velocity ? `${flightData.velocity} mph` : 'N/A'}</strong></div>
                <div><span>Heading</span><strong>{flightData.heading ? `${flightData.heading}°` : 'N/A'}</strong></div>
              </div>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

export default Upload;