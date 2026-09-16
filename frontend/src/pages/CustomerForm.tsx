import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import apiClient from '../api/axios';
import { Customer } from '../types';
import { TextField, Button, Container, Typography, Box, CircularProgress } from '@mui/material';

const CustomerForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [customer, setCustomer] = useState<Partial<Customer>>({
    name: '',
    email: '',
    phone_number: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      setLoading(true);
      const fetchCustomer = async () => {
        try {
          const response = await apiClient.get(`/api/v1/crm/customers/${id}/`);
          setCustomer(response.data);
        } catch (err: any) {
          setError(err.response?.data?.detail || 'Failed to fetch customer');
        } finally {
          setLoading(false);
        }
      };
      fetchCustomer();
    }
  }, [id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCustomer({ ...customer, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (id) {
        await apiClient.put(`/api/v1/crm/customers/${id}/`, customer);
      } else {
        await apiClient.post('/v1/crm/customers/', customer);
      }
      navigate('/customers');
    } catch (err) {
      setError('Failed to save customer');
    } finally {
      setLoading(false);
    }
  };

  if (loading && id) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  return (
    <Container maxWidth="sm">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {id ? 'Edit Customer' : 'New Customer'}
        </Typography>
        <form onSubmit={handleSubmit}>
          <Box sx={{ mb: 2 }}>
            <TextField
              fullWidth
              label="Customer Name"
              name="name"
              value={customer.name ?? ''}
              onChange={handleChange}
              variant="outlined"
            />
          </Box>
          <Box sx={{ mb: 2 }}>
            <TextField
              fullWidth
              label="Email"
              name="email"
              type="email"
              value={customer.email ?? ''}
              onChange={handleChange}
              variant="outlined"
            />
          </Box>
          <Box sx={{ mb: 2 }}>
            <TextField
              fullWidth
              label="Phone Number"
              name="phone_number"
              value={customer.phone_number}
              onChange={handleChange}
              variant="outlined"
            />
          </Box>
          <Button type="submit" variant="contained" color="primary" disabled={loading}>
            {loading ? <CircularProgress size={24} /> : 'Save'}
          </Button>
        </form>
      </Box>
    </Container>
  );
};

export default CustomerForm;