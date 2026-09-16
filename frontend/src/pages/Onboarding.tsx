import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/axios';
import { useAuth } from '../context/AuthContext';
import {
  Button,
  Typography,
  Box,
  TextField,
  Container,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material';

const Onboarding: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, loading: authLoading, markOnboardingComplete, logout } = useAuth();
  const [formData, setFormData] = useState({
    name: '',
    business_type: '',
    phone: '',
    email: '',
    address: '',
    county: '',
    country: 'Kenya',
    currency: 'KES',
    timezone: 'Africa/Nairobi',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/login', { replace: true });
      return;
    }

    if (authLoading || !isAuthenticated) return;

    const loadBusiness = async () => {
      try {
        const response = await apiClient.get('/auth/business/');
        if (response.data.has_completed_onboarding) {
          navigate('/', { replace: true });
          return;
        }
        setFormData((current) => ({
          ...current,
          ...response.data,
          email: response.data.email || current.email,
        }));
      } catch {
        // A new account can still complete the form manually.
      }
    };
    loadBusiness();
  }, [authLoading, isAuthenticated, navigate]);

  if (authLoading || !isAuthenticated) {
    return <CircularProgress />;
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const businessName = formData.name.trim();
    const businessEmail = formData.email.trim();
    if (!businessName || !businessEmail) {
      setError('Business name and email are required.');
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(businessEmail)) {
      setError('Enter a valid business email address.');
      return;
    }
    setError(null);
    setLoading(true);
    try {
      await apiClient.put('/auth/onboarding/', {
        ...formData,
        name: businessName,
        email: businessEmail,
      });
      markOnboardingComplete();
      navigate('/');
    } catch (err: unknown) {
      let errorMessage = 'Failed to complete onboarding';
      if (typeof err === 'object' && err !== null && 'response' in err) {
        const response = (err as any).response;
        if (response?.data?.detail) {
          errorMessage = response.data.detail;
        } else if (response?.data && typeof response.data === 'object') {
          errorMessage = Object.entries(response.data)
            .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
            .join(' ');
        }
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="sm" sx={{ mt: 4 }}>
      <Paper variant="outlined" sx={{ my: { xs: 3, md: 6 }, p: { xs: 2, md: 3 } }}>
        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button type="button" color="error" variant="outlined" onClick={logout}>
            Logout
          </Button>
        </Box>
        <Typography component="h1" variant="h4" align="center">
          Welcome! Let's get you set up.
        </Typography>
        <form onSubmit={handleSubmit} noValidate>
          <TextField fullWidth label="Business Name" name="name" value={formData.name} onChange={handleChange} margin="normal" error={Boolean(error && !formData.name.trim())} />
          <TextField fullWidth label="Business Type" name="business_type" value={formData.business_type} onChange={handleChange} margin="normal" />
          <TextField fullWidth label="Phone Number" name="phone" value={formData.phone} onChange={handleChange} margin="normal" />
          <TextField fullWidth label="Email" name="email" type="email" value={formData.email} onChange={handleChange} margin="normal" error={Boolean(error && !formData.email.trim())} />
          <TextField fullWidth label="Address" name="address" value={formData.address} onChange={handleChange} margin="normal" />
          <TextField fullWidth label="County" name="county" value={formData.county} onChange={handleChange} margin="normal" />
          <TextField fullWidth label="Country" name="country" value={formData.country} onChange={handleChange} margin="normal" />
          <TextField fullWidth label="Currency" name="currency" value={formData.currency} onChange={handleChange} margin="normal" />
          <TextField fullWidth required label="Timezone" name="timezone" value={formData.timezone} onChange={handleChange} margin="normal" />
          {error && <Alert severity="error">{error}</Alert>}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
            <Button variant="contained" color="primary" type="submit" disabled={loading}>
              {loading ? <CircularProgress size={24} /> : 'Complete setup'}
            </Button>
          </Box>
        </form>
      </Paper>
    </Container>
  );
};

export default Onboarding;