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
} from '@mui/material';

const WhatsAppInbox: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const response = await apiClient.get('/v1/conversations/');
        setConversations(response.data.results);
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
  }, []);

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
          <ConversationList
            conversations={conversations}
            onSelectConversation={setSelectedConversation}
            selectedConversation={selectedConversation}
          />
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