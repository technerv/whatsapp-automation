import React, { useState, useEffect } from 'react';
import apiClient from '../api/axios';
import toast from 'react-hot-toast';
import {
  Tabs,
  Tab,
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  CircularProgress,
  Grid,
} from '@mui/material';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const Settings: React.FC = () => {
  const [value, setValue] = useState(0);
  const [profile, setProfile] = useState({
    first_name: '',
    last_name: '',
    email: '',
  });
  const [business, setBusiness] = useState({
    name: '',
    business_type: '',
    phone: '',
    email: '',
    address: '',
    county: '',
    country: '',
    currency: '',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [profileRes, businessRes] = await Promise.all([
          apiClient.get('/auth/me/'),
          apiClient.get('/auth/business/'),
        ]);
        setProfile(profileRes.data);
        setBusiness(businessRes.data);
      } catch (err: unknown) {
        let errorMessage = 'Failed to fetch settings';
        if (typeof err === 'object' && err !== null && 'response' in err) {
          const response = (err as any).response;
          if (response?.data?.detail) {
            errorMessage = response.data.detail;
          }
        }
        toast.error(errorMessage);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  const handleProfileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  const handleBusinessChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setBusiness({ ...business, [e.target.name]: e.target.value });
  };

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.patch('/auth/me/update/', profile);
      toast.success('Profile updated successfully');
    } catch (err: unknown) {
      let errorMessage = 'Failed to update profile';
      if (typeof err === 'object' && err !== null && 'response' in err) {
        const response = (err as any).response;
        if (response?.data?.detail) {
          errorMessage = response.data.detail;
        }
      }
      toast.error(errorMessage);
    }
  };

  const handleBusinessSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.put('/auth/business/', business);
      toast.success('Business settings updated successfully');
    } catch (err: unknown) {
      let errorMessage = 'Failed to update business settings';
      if (typeof err === 'object' && err !== null && 'response' in err) {
        const response = (err as any).response;
        if (response?.data?.detail) {
          errorMessage = response.data.detail;
        }
      }
      toast.error(errorMessage);
    }
  };

  if (loading) {
    return <CircularProgress />;
  }

  return (
    <Paper>
      <Typography variant="h6" component="h1" sx={{ p: 2 }}>
        Settings
      </Typography>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={value} onChange={handleTabChange} aria-label="settings tabs">
          <Tab label="My Profile" id="settings-tab-0" />
          <Tab label="Business Settings" id="settings-tab-1" />
        </Tabs>
      </Box>
      <TabPanel value={value} index={0}>
        <form onSubmit={handleProfileSubmit}>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="First Name"
                name="first_name"
                value={profile.first_name}
                onChange={handleProfileChange}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Last Name"
                name="last_name"
                value={profile.last_name}
                onChange={handleProfileChange}
              />
            </Grid>
            <Grid size={12}>
              <TextField
                fullWidth
                label="Email"
                name="email"
                type="email"
                value={profile.email}
                onChange={handleProfileChange}
              />
            </Grid>
            <Grid size={12}>
              <Button type="submit" variant="contained">Save Profile</Button>
            </Grid>
          </Grid>
        </form>
      </TabPanel>
      <TabPanel value={value} index={1}>
        <form onSubmit={handleBusinessSubmit}>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Business Name"
                name="name"
                value={business.name}
                onChange={handleBusinessChange}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Business Type"
                name="business_type"
                value={business.business_type}
                onChange={handleBusinessChange}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Phone Number"
                name="phone"
                value={business.phone}
                onChange={handleBusinessChange}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Email"
                name="email"
                type="email"
                value={business.email}
                onChange={handleBusinessChange}
              />
            </Grid>
            <Grid size={12}>
              <TextField
                fullWidth
                label="Address"
                name="address"
                value={business.address}
                onChange={handleBusinessChange}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="County"
                name="county"
                value={business.county}
                onChange={handleBusinessChange}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Country"
                name="country"
                value={business.country}
                onChange={handleBusinessChange}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Currency"
                name="currency"
                value={business.currency}
                onChange={handleBusinessChange}
              />
            </Grid>
            <Grid size={12}>
              <Button type="submit" variant="contained">Save Business Settings</Button>
            </Grid>
          </Grid>
        </form>
      </TabPanel>
    </Paper>
  );
};

export default Settings;