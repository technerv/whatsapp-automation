import React from 'react';
import { Conversation } from '../../types';
import {
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Typography,
  Box,
} from '@mui/material';

interface ConversationListProps {
  conversations: Conversation[];
  onSelectConversation: (conversation: Conversation) => void;
  selectedConversation: Conversation | null;
}

const ConversationList: React.FC<ConversationListProps> = ({
  conversations,
  onSelectConversation,
  selectedConversation,
}) => {
  return (
    <List sx={{ height: '100%', overflowY: 'auto' }}>
      {conversations.map((conversation) => (
        <ListItem key={conversation.id} disablePadding>
          <ListItemButton
            selected={selectedConversation?.id === conversation.id}
            onClick={() => onSelectConversation(conversation)}
          >
            <ListItemText
              primary={conversation.customer.name}
              secondary={
                <Typography
                  sx={{ display: 'inline' }}
                  component="span"
                  variant="body2"
                  color="text.primary"
                >
                  {conversation.last_message?.content}
                </Typography>
              }
            />
            <Box sx={{ textAlign: 'right' }}>
              {conversation.unread_count > 0 && (
                <Box>
                  <Typography variant="caption" color="primary">
                  {conversation.unread_count} unread
                  </Typography>
                </Box>
              )}
              <Typography variant="caption" color="text.secondary">
                {new Date(conversation.last_message_at).toLocaleTimeString()}
              </Typography>
            </Box>
          </ListItemButton>
        </ListItem>
      ))}
    </List>
  );
};

export default ConversationList;