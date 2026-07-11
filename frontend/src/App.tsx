import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Login from './pages/Login';
import Register from './pages/Register';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Activity, MessageSquare, LogOut } from 'lucide-react';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  return <>{children}</>;
};

function Layout({ children }: { children: React.ReactNode }) {
  const { logout } = useAuth();
  
  return (
      <div className="min-h-screen flex flex-col bg-slate-50">
        <header className="bg-white shadow-sm border-b border-slate-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16 items-center">
              <div className="flex items-center gap-2">
                <Activity className="h-8 w-8 text-primary-600" />
                <span className="font-bold text-xl text-slate-900">AI Medical Assistant</span>
              </div>
              <nav className="flex items-center gap-4">
                <Link to="/" className="text-slate-600 hover:text-primary-600 font-medium transition-colors">
                  Dashboard
                </Link>
                <Link to="/chat" className="flex items-center gap-1 text-slate-600 hover:text-primary-600 font-medium transition-colors">
                  <MessageSquare className="h-4 w-4" />
                  Chat
                </Link>
                <button onClick={logout} className="flex items-center gap-1 text-slate-600 hover:text-red-600 font-medium transition-colors ml-4 border-l border-slate-200 pl-4">
                  <LogOut className="h-4 w-4" />
                  Logout
                </button>
              </nav>
            </div>
          </div>
        </header>

        {/* Disclaimer Banner */}
        <div className="bg-amber-50 border-b border-amber-200 py-3 px-4 text-center">
          <p className="text-sm text-amber-800 font-medium">
            <span className="font-bold uppercase mr-1">Disclaimer:</span>
            For Educational Purposes Only. Not a substitute for professional medical advice, diagnosis, or treatment.
          </p>
        </div>

        <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </div>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={<ProtectedRoute><Layout><Dashboard /></Layout></ProtectedRoute>} />
          <Route path="/chat" element={<ProtectedRoute><Layout><Chat /></Layout></ProtectedRoute>} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
