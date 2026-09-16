export interface Customer {
  id: string;
  name: string;
  email: string | null;
  phone_number: string;
}

export interface WhatsAppMessage {
  id: string;
  content: string;
  direction: 'inbound' | 'outbound';
  timestamp: string;
}

export interface Conversation {
  id: string;
  customer: Customer;
  last_message_at: string;
  last_message: WhatsAppMessage | null;
}

export interface Order {
  id: string;
  customer: Customer;
  total_amount: number | string;
  status: string;
  order_date: string;
}

export interface WorkflowNode {
  key: string;
  action: string;
  config?: Record<string, unknown>;
}

export interface Workflow {
  id: string;
  name: string;
  trigger_type: string;
  definition: { nodes: WorkflowNode[] };
  status: 'draft' | 'active' | 'paused';
  version: number;
  created_at: string;
  updated_at: string;
}