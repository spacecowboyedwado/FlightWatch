import {BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import Navbar from './components/Navbar.jsx'
import Home from './views/Home.jsx';
import Docs from './views/Docs.jsx'
import Upload from './views/Upload.jsx';


function App() {
  return (
      <Router>
    <div className="app-container">
        {/* The navbar displays globally across all pages */}
        <Navbar />

        {/* Routes manages which page view gets loaded depending on the address bar */}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/docs" element={<Docs />} />
          <Route path="/upload" element={<Upload/> } />
        </Routes>
      </div>
  </Router>
  );
}

export default App;