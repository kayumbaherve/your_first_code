/**
 * AI Interior Design Assistant - Main React Application
 */

import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, CircularProgress } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
import { HelmetProvider } from 'react-helmet-async';
import { Toaster } from 'react-hot-toast';

// Context Providers
import { AuthProvider } from './contexts/AuthContext';
import { ProjectProvider } from './contexts/ProjectContext';

// Components
import Navbar from './components/Layout/Navbar';
import Sidebar from './components/Layout/Sidebar';
import LoadingScreen from './components/Common/LoadingScreen';
import ErrorBoundary from './components/Common/ErrorBoundary';

// Pages (Lazy loaded for better performance)
const Dashboard = React.lazy(() => import('./components/Dashboard/Dashboard'));
const RoomScanner = React.lazy(() => import('./components/RoomScanner/RoomScanner'));
const Viewer3D = React.lazy(() => import('./components/3DViewer/Viewer3D'));
const VirtualStaging = React.lazy(() => import('./components/VirtualStaging/VirtualStaging'));
const ProjectManager = React.lazy(() => import('./components/ProjectManager/ProjectManager'));
const UserProfile = React.lazy(() => import('./components/User/UserProfile'));
const Login = React.lazy(() => import('./components/Auth/Login'));
const Register = React.lazy(() => import('./components/Auth/Register'));

// Styles
import './styles/main.css';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Create Material-UI theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2563eb',
      light: '#60a5fa',
      dark: '#1d4ed8',
    },
    secondary: {
      main: '#7c3aed',
      light: '#a78bfa',
      dark: '#5b21b6',
    },
    background: {
      default: '#f8fafc',
      paper: '#ffffff',
    },
    text: {
      primary: '#1e293b',
      secondary: '#64748b',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      lineHeight: 1.3,
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          borderRadius: 8,
          padding: '10px 20px',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
          borderRadius: 12,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        },
      },
    },
  },
});

// Loading fallback component
const SuspenseFallback = () => (
  <Box
    display="flex"
    justifyContent="center"
    alignItems="center"
    minHeight="60vh"
  >
    <CircularProgress size={40} />
  </Box>
);

// Protected Route component
const ProtectedRoute = ({ children }) => {
  // This would check authentication status
  // For now, we'll assume user is authenticated
  const isAuthenticated = true; // Replace with actual auth check
  
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// Main App Layout
const AppLayout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = React.useState(false);

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          pt: 8, // Account for navbar height
          px: { xs: 2, sm: 3 },
          pb: 3,
          backgroundColor: 'background.default',
          minHeight: '100vh',
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

// Main App Component
function App() {
  return (
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <ErrorBoundary>
            <AuthProvider>
              <ProjectProvider>
                <Router>
                  <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
                    <Routes>
                      {/* Public Routes */}
                      <Route
                        path="/login"
                        element={
                          <Suspense fallback={<LoadingScreen />}>
                            <Login />
                          </Suspense>
                        }
                      />
                      <Route
                        path="/register"
                        element={
                          <Suspense fallback={<LoadingScreen />}>
                            <Register />
                          </Suspense>
                        }
                      />

                      {/* Protected Routes */}
                      <Route
                        path="/"
                        element={
                          <ProtectedRoute>
                            <AppLayout>
                              <Suspense fallback={<SuspenseFallback />}>
                                <Dashboard />
                              </Suspense>
                            </AppLayout>
                          </ProtectedRoute>
                        }
                      />
                      
                      <Route
                        path="/dashboard"
                        element={
                          <ProtectedRoute>
                            <AppLayout>
                              <Suspense fallback={<SuspenseFallback />}>
                                <Dashboard />
                              </Suspense>
                            </AppLayout>
                          </ProtectedRoute>
                        }
                      />

                      <Route
                        path="/scan"
                        element={
                          <ProtectedRoute>
                            <AppLayout>
                              <Suspense fallback={<SuspenseFallback />}>
                                <RoomScanner />
                              </Suspense>
                            </AppLayout>
                          </ProtectedRoute>
                        }
                      />

                      <Route
                        path="/3d-viewer"
                        element={
                          <ProtectedRoute>
                            <AppLayout>
                              <Suspense fallback={<SuspenseFallback />}>
                                <Viewer3D />
                              </Suspense>
                            </AppLayout>
                          </ProtectedRoute>
                        }
                      />

                      <Route
                        path="/staging"
                        element={
                          <ProtectedRoute>
                            <AppLayout>
                              <Suspense fallback={<SuspenseFallback />}>
                                <VirtualStaging />
                              </Suspense>
                            </AppLayout>
                          </ProtectedRoute>
                        }
                      />

                      <Route
                        path="/projects"
                        element={
                          <ProtectedRoute>
                            <AppLayout>
                              <Suspense fallback={<SuspenseFallback />}>
                                <ProjectManager />
                              </Suspense>
                            </AppLayout>
                          </ProtectedRoute>
                        }
                      />

                      <Route
                        path="/profile"
                        element={
                          <ProtectedRoute>
                            <AppLayout>
                              <Suspense fallback={<SuspenseFallback />}>
                                <UserProfile />
                              </Suspense>
                            </AppLayout>
                          </ProtectedRoute>
                        }
                      />

                      {/* Catch all route */}
                      <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                  </Box>

                  {/* Global Toast Notifications */}
                  <Toaster
                    position="top-right"
                    toastOptions={{
                      duration: 4000,
                      style: {
                        background: '#363636',
                        color: '#fff',
                        borderRadius: '8px',
                      },
                      success: {
                        iconTheme: {
                          primary: '#4ade80',
                          secondary: '#fff',
                        },
                      },
                      error: {
                        iconTheme: {
                          primary: '#ef4444',
                          secondary: '#fff',
                        },
                      },
                    }}
                  />
                </Router>
              </ProjectProvider>
            </AuthProvider>
          </ErrorBoundary>
        </ThemeProvider>
        
        {/* React Query DevTools (only in development) */}
        {process.env.NODE_ENV === 'development' && (
          <ReactQueryDevtools initialIsOpen={false} />
        )}
      </QueryClientProvider>
    </HelmetProvider>
  );
}

export default App;

