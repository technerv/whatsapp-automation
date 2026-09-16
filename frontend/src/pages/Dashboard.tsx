import React, { useState, useEffect } from 'react';
import apiClient from '../api/axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Grid, Paper, Typography, Box, CircularProgress, Alert } from '@mui/material';

interface DashboardStats {
  customer_count: number;
  lead_count: number;
}

interface DailySignup {
  date: string;
  customers: number;
  leads: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [dailySignups, setDailySignups] = useState<DailySignup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsResponse, dailySignupsResponse] = await Promise.all([
          apiClient.get('/v1/crm/dashboard-stats/'),
          apiClient.get('/v1/crm/daily-signups/'),
        ]);
        setStats(statsResponse.data);
        setDailySignups(dailySignupsResponse.data);
      } catch (err: unknown) {
        let errorMessage = 'Failed to fetch dashboard data';
        if (typeof err === 'object' && err !== null && 'response' in err) {
          const response = (err as any).response;
          if (response?.data?.detail) {
            errorMessage = response.data.detail;
          }
        }
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 6, lg: 3 }}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Total Customers
            </Typography>
            <Typography component="p" variant="h4">
              {stats?.customer_count}
            </Typography>
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, md: 6, lg: 3 }}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Total Leads
            </Typography>
            <Typography component="p" variant="h4">
              {stats?.lead_count}
            </Typography>
          </Paper>
        </Grid>
        {/* Add more stat cards as we build out the features */}
        <Grid size={12}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Signups in the Last 7 Days
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={dailySignups}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="customers" stroke="#8884d8" />
                <Line type="monotone" dataKey="leads" stroke="#82ca9d" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;