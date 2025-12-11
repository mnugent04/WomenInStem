import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import People from './pages/People';
import Events from './pages/Events';
import SmallGroups from './pages/SmallGroups';
import Search from './pages/Search';
import './App.css';

function App() {
  return (
    <Router>
      <div className="container-fluid">
        <div className="grid">
          <aside className="sidebar">
            <nav>
              <ul>
                <li>
                  <h3>Youth Group</h3>
                </li>
              </ul>
              <ul>
                <li>
                  <Link to="/" role="button" >Home</Link>
                </li>
                <li>
                  <Link to="/people" role="button">People</Link>
                </li>
                <li>
                  <Link to="/events" role="button">Events</Link>
                </li>
                <li>
                  <Link to="/small-groups" role="button">Small Groups</Link>
                </li>
                <li>
                  <Link to="/search" role="button">Search</Link>
                </li>
              </ul>
            </nav>
          </aside>
          <main>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/people" element={<People />} />
              <Route path="/events" element={<Events />} />
              <Route path="/small-groups" element={<SmallGroups />} />
              <Route path="/search" element={<Search />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}


export default App;
