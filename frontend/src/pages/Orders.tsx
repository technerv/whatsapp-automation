import React, { useState, useEffect } from 'react';
import apiClient from '../api/axios';
import { Order } from '../types';
import toast from 'react-hot-toast';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  CircularProgress,
  Pagination,
  Box,
} from '@mui/material';

const Orders: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    const fetchOrders = async () => {
      setLoading(true);
      try {
        const response = await apiClient.get('/v1/orders/orders/', {
          params: { page: currentPage },
        });
        setOrders(response.data.results);
        setTotalPages(Math.ceil(response.data.count / 10)); // Assuming 10 items per page
      } catch (err: unknown) {
        let errorMessage = 'Failed to fetch orders';
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

    fetchOrders();
  }, [currentPage]);

  if (loading) {
    return <CircularProgress />;
  }

  return (
    <Paper>
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" component="h1">
          Orders
        </Typography>
      </Box>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Order ID</TableCell>
              <TableCell>Customer</TableCell>
              <TableCell>Total</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Date</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {orders.map((order) => (
              <TableRow key={order.id}>
                <TableCell>{order.id}</TableCell>
                <TableCell>{order.customer.name}</TableCell>
                <TableCell>{order.total_amount}</TableCell>
                <TableCell>{order.status}</TableCell>
                <TableCell>{new Date(order.order_date).toLocaleDateString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Box sx={{ p: 2, display: 'flex', justifyContent: 'center' }}>
        <Pagination
          count={totalPages}
          page={currentPage}
          onChange={(_, page) => setCurrentPage(page)}
        />
      </Box>
    </Paper>
  );
};

export default Orders;