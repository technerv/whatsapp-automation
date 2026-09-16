import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import AppLayout from './components/AppLayout';
import Dashboard from './pages/Dashboard';
import WhatsAppInbox from './pages/WhatsAppInbox';
import Customers from './pages/Customers';
import CustomerForm from './pages/CustomerForm';
import Orders from './pages/Orders';
import Settings from './pages/Settings';
import Workflows from './pages/Workflows';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import Onboarding from './pages/Onboarding';
import { useAuth } from './context/AuthContext';
import { Toaster } from 'react-hot-toast';

const PrivateRoute = ({ children }: { children: JSX.Element }) => {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  const onboardingComplete = user?.business?.has_completed_onboarding ?? user?.has_completed_onboarding;
  if (!onboardingComplete) {
    return <Navigate to="/onboarding" replace />;
  }

  return children;
};

function App() {
  return (
    <Router>
      <Toaster />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/onboarding" element={<Onboarding />} />
        <Route
          path="/*"
          element={
            <PrivateRoute>
              <AppLayout>
                <Routes>
                  <Route index element={<Dashboard />} />
                  <Route path="whatsapp" element={<WhatsAppInbox />} />
                  <Route path="customers" element={<Customers />} />
                  <Route path="customers/new" element={<CustomerForm />} />
                  <Route path="customers/:id/edit" element={<CustomerForm />} />
                  <Route path="orders" element={<Orders />} />
                  <Route path="settings" element={<Settings />} />
                  <Route path="workflows" element={<Workflows />} />
                </Routes>
              </AppLayout>
            </PrivateRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;