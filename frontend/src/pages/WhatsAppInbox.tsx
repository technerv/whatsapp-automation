import React, { useState, useEffect } from 'react';
import apiClient from '../api/axios';
import { Conversation } from '../types';
import ConversationList from '../components/whatsapp/ConversationList';
import MessageView from '../components/whatsapp/MessageView';
import Chatbot from '../components/Chatbot';
import toast from 'react-hot-toast';
import {
  Grid,
  Paper,
  Tabs,
  Tab,
  Box,
  Typography,
  CircularProgress,
  TextField,
  MenuItem,
  Select,
  InputLabel,
  FormControl,
} from '@mui/material';

const WhatsAppInbox: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const response = await apiClient.get('/v1/conversations/', {
          params: { search: search || undefined, status: statusFilter || undefined },
        });
        setConversations(response.data.results ?? response.data);
      } catch (err: unknown) {
        let errorMessage = 'Failed to fetch conversations';
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

    fetchConversations();
  }, [search, statusFilter]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  if (loading) {
    return <CircularProgress />;
  }

  return (
    <Grid container component={Paper} sx={{ height: 'calc(100vh - 64px)' }}>
      <Grid size={{ xs: 12, md: 4 }} sx={{ borderRight: { md: '1px solid #ddd' } }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={handleTabChange} variant="fullWidth">
            <Tab label="Inbox" />
            <Tab label="AI Assistant" />
          </Tabs>
        </Box>
        {activeTab === 0 && (
          <>
            <Box sx={{ p: 2, display: 'flex', gap: 1 }}>
              <TextField size="small" fullWidth label="Search" value={search} onChange={(event) => setSearch(event.target.value)} />
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel id="conversation-status-label">Status</InputLabel>
                <Select labelId="conversation-status-label" value={statusFilter} label="Status" onChange={(event) => setStatusFilter(event.target.value)}>
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="open">Open</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="closed">Closed</MenuItem>
                </Select>
              </FormControl>
            </Box>
            <ConversationList
              conversations={conversations}
              onSelectConversation={setSelectedConversation}
              selectedConversation={selectedConversation}
            />
          </>
        )}
      </Grid>
      <Grid size={{ xs: 12, md: 8 }}>
        {activeTab === 0 ? (
          selectedConversation ? (
            <MessageView conversation={selectedConversation} />
          ) : (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
              }}
            >
              <Typography color="text.secondary">
                Select a conversation to start messaging
              </Typography>
            </Box>
          )
        ) : (
          <Chatbot />
        )}
      </Grid>
    </Grid>
  );
};

export default WhatsAppInbox;