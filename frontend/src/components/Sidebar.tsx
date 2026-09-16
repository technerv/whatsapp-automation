import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Toolbar, Box, Button } from '@mui/material';
import { Dashboard, WhatsApp, People, ShoppingCart, Settings, AccountTree } from '@mui/icons-material';

const drawerWidth = 240;

const Sidebar: React.FC = () => {
  const { logout } = useAuth();

  const menuItems = [
    { text: 'Dashboard', icon: <Dashboard />, path: '/' },
    { text: 'WhatsApp Inbox', icon: <WhatsApp />, path: '/whatsapp' },
    { text: 'Customers', icon: <People />, path: '/customers' },
    { text: 'Orders', icon: <ShoppingCart />, path: '/orders' },
    { text: 'Workflows', icon: <AccountTree />, path: '/workflows' },
    { text: 'Settings', icon: <Settings />, path: '/settings' },
  ];

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
      }}
    >
      <Toolbar />
      <Box sx={{ overflow: 'auto' }}>
        <List>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton component={Link} to={item.path}>
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>
      <Box sx={{ position: 'absolute', bottom: 0, width: '100%', p: 2 }}>
        <Button variant="contained" color="error" onClick={logout} fullWidth>
          Logout
        </Button>
      </Box>
    </Drawer>
  );
};

export default Sidebar;