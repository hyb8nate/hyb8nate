import React, { ReactNode } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

interface LayoutProps {
  children: ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      <nav className="bg-white/80 backdrop-blur-md shadow-soft border-b border-gray-200/50 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <Link to="/dashboard" className="flex items-center gap-3 group">
                <div className="w-10 h-10 rounded-lg bg-gradient-primary p-2 shadow-md group-hover:shadow-glow transition-all duration-200">
                  <svg className="w-full h-full text-white" viewBox="0 0 200 200" fill="currentColor">
                    <ellipse cx="100" cy="120" rx="45" ry="40"/>
                    <circle cx="100" cy="80" r="30"/>
                    <circle cx="80" cy="65" r="12"/>
                    <circle cx="120" cy="65" r="12"/>
                    <ellipse cx="92" cy="78" rx="6" ry="3" fill="#FFFFFF"/>
                    <ellipse cx="108" cy="78" rx="6" ry="3" fill="#FFFFFF"/>
                    <ellipse cx="100" cy="88" rx="4" ry="3" fill="#FFFFFF"/>
                  </svg>
                </div>
                <div>
                  <h1 className="text-xl font-bold bg-gradient-primary bg-clip-text text-transparent">
                    hyp8nate
                  </h1>
                  <p className="text-xs text-gray-500">K8s Hibernation</p>
                </div>
              </Link>
            </div>

            <div className="flex items-center gap-4">
              <span className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-gradient-accent text-white shadow-glow-accent">
                Administrator
              </span>

              <button
                onClick={handleLogout}
                className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all duration-200"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
};
