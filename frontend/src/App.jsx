import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import ProjectsList from './components/projects/ProjectsList';
import KanbanBoard from './components/issues/KanbanBoard';
import AppNavbar from './components/common/Navbar';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <>
                  <AppNavbar />
                  <ProjectsList />
                </>
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/projects/:projectId"
            element={
              <ProtectedRoute>
                <>
                  <AppNavbar />
                  <KanbanBoard />
                </>
              </ProtectedRoute>
            }
          />

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;