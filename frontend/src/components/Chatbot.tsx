import React, { useState, useRef, useEffect } from 'react';
import apiClient from '../api/axios';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  CircularProgress,
  AppBar,
  Toolbar,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

interface Message {
  text: string;
  sender: 'user' | 'bot';
}

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (input.trim() === '') return;

    const newMessages: Message[] = [...messages, { text: input, sender: 'user' }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      const response = await apiClient.post('/v1/ai/dialogflow-webhook/', {
        text: input,
        session: 'default_session_id', // You can use a unique session ID for each user
      });
      const botMessage: Message = {
        text: response.data.fulfillmentText,
        sender: 'bot',
      };
      setMessages([...newMessages, botMessage]);
    } catch (error: unknown) {
      let errorMessageText = 'Error: Could not connect to the chatbot.';
      if (typeof error === 'object' && error !== null && 'response' in error) {
        const response = (error as any).response;
        if (response?.data?.detail) {
          errorMessageText = response.data.detail;
        }
      }
      const errorMessage: Message = {
        text: errorMessageText,
        sender: 'bot',
      };
      setMessages([...newMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar>
          <Typography variant="h6">AI Assistant</Typography>
        </Toolbar>
      </AppBar>
      <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 2 }}>
        {messages.map((message, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
              mb: 1,
            }}
          >
            <Paper
              elevation={1}
              sx={{
                p: 1,
                bgcolor: message.sender === 'user' ? 'primary.main' : 'grey.300',
                color: message.sender === 'user' ? 'primary.contrastText' : 'text.primary',
                maxWidth: '70%',
              }}
            >
              <Typography variant="body1">{message.text}</Typography>
            </Paper>
          </Box>
        ))}
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 1 }}>
            <CircularProgress size={24} />
          </Box>
        )}
        <div ref={messagesEndRef} />
      </Box>
      <Box sx={{ p: 2, borderTop: '1px solid #ddd' }}>
        <Box sx={{ display: 'flex' }}>
          <TextField
            fullWidth
            variant="outlined"
            size="small"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message..."
          />
          <Button
            variant="contained"
            color="primary"
            onClick={handleSend}
            sx={{ ml: 1 }}
            disabled={loading}
          >
            <SendIcon />
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default Chatbot;