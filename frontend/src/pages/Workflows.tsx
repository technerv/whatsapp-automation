import React, { useEffect, useState } from 'react';
import apiClient from '../api/axios';
import toast from 'react-hot-toast';
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import PauseIcon from '@mui/icons-material/Pause';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { Workflow } from '../types';

const triggers = ['contact.created', 'message.received', 'order.created', 'payment.successful'];

const Workflows: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [name, setName] = useState('');
  const [triggerType, setTriggerType] = useState(triggers[0]);

  const fetchWorkflows = async () => {
    try {
      const response = await apiClient.get('/v1/ai/workflows/');
      setWorkflows(response.data.results ?? response.data);
    } catch {
      setError('Failed to load workflows');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const createWorkflow = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await apiClient.post('/v1/ai/workflows/', {
        name,
        trigger_type: triggerType,
        definition: {
          nodes: [{
            key: 'message',
            action: 'send_whatsapp_message',
            config: { text: 'Thanks for reaching out. We will be with you shortly.' },
          }],
        },
      });
      toast.success('Workflow created as a draft');
      setDialogOpen(false);
      setName('');
      await fetchWorkflows();
    } catch {
      toast.error('Could not create workflow');
    }
  };

  const updateStatus = async (workflow: Workflow) => {
    const action = workflow.status === 'active' ? 'pause' : 'publish';
    try {
      await apiClient.post(`/v1/ai/workflows/${workflow.id}/${action}/`);
      await fetchWorkflows();
      toast.success(action === 'publish' ? 'Workflow published' : 'Workflow paused');
    } catch {
      toast.error('Could not update workflow');
    }
  };

  if (loading) return <CircularProgress />;

  return (
    <Box>
      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, justifyContent: 'space-between', alignItems: { sm: 'center' }, gap: 2, mb: 3 }}>
        <Box>
          <Typography variant="h4">Workflows</Typography>
          <Typography color="text.secondary">Automate customer journeys from business events.</Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setDialogOpen(true)}>
          New workflow
        </Button>
      </Box>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {workflows.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>No workflows yet</Typography>
          <Typography color="text.secondary">Create a draft to start shaping an automation.</Typography>
        </Paper>
      ) : (
        <Stack spacing={2}>
          {workflows.map((workflow) => (
            <Paper key={workflow.id} sx={{ p: 2.5 }}>
              <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, justifyContent: 'space-between', gap: 2 }}>
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="h6">{workflow.name}</Typography>
                    <Chip size="small" label={workflow.status} color={workflow.status === 'active' ? 'success' : 'default'} />
                  </Box>
                  <Typography color="text.secondary" sx={{ mt: 0.5 }}>
                    Trigger: {workflow.trigger_type} · Version {workflow.version} · {workflow.definition.nodes.length} node(s)
                  </Typography>
                </Box>
                <Button
                  variant={workflow.status === 'active' ? 'outlined' : 'contained'}
                  startIcon={workflow.status === 'active' ? <PauseIcon /> : <PlayArrowIcon />}
                  onClick={() => updateStatus(workflow)}
                >
                  {workflow.status === 'active' ? 'Pause' : 'Publish'}
                </Button>
              </Box>
            </Paper>
          ))}
        </Stack>
      )}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} fullWidth maxWidth="sm">
        <Box component="form" onSubmit={createWorkflow}>
          <DialogTitle>Create workflow</DialogTitle>
          <DialogContent>
            <TextField autoFocus fullWidth required label="Workflow name" value={name} onChange={(event) => setName(event.target.value)} sx={{ mt: 1, mb: 2 }} />
            <FormControl fullWidth>
              <InputLabel id="workflow-trigger-label">Trigger</InputLabel>
              <Select labelId="workflow-trigger-label" value={triggerType} label="Trigger" onChange={(event) => setTriggerType(event.target.value)}>
                {triggers.map((trigger) => <MenuItem key={trigger} value={trigger}>{trigger}</MenuItem>)}
              </Select>
            </FormControl>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Create draft</Button>
          </DialogActions>
        </Box>
      </Dialog>
    </Box>
  );
};

export default Workflows;