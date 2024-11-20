import * as React from 'react';
import axios from 'axios';
import { 
  Box,
  Card,
  Typography,
  Button,
  CircularProgress,
  Alert,
  useTheme,
  FormControl,
  Select,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Fade
} from '@mui/material';
import { 
  Refresh as RefreshIcon,
  Mail as MailIcon,
  ErrorOutline as ErrorIcon,
  FilterList as FilterIcon,
  FormatListNumbered as ListIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';

export default function EmailReader() {
  const [data, setData] = React.useState([]);
  const [error, setError] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [filter, setFilter] = React.useState('ALL');
  const [limit, setLimit] = React.useState(50);
  const theme = useTheme();

  const fetchData = async (keyword = 'all', emailLimit = limit) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        `http://${process.env.REACT_APP_API_URL}:${process.env.REACT_APP_API_PORT}/emails/${keyword.toLowerCase()}?limit=${emailLimit}`
      );
      setData(response.data);
    } catch (err) {
      console.error(err);
      setError('Unable to fetch emails. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchData();
  }, []);

  const handleFilterChange = async (event) => {
    const newFilter = event.target.value;
    setFilter(newFilter);
    await fetchData(newFilter, limit);
  };

  const handleLimitChange = async (event) => {
    const newLimit = event.target.value;
    setLimit(newLimit);
    await fetchData(filter, newLimit);
  };

  const handleEmailClick = (email, index) => {
    console.log(`Email ${index + 1} clicked`, email);
  };

  const handleRefresh = () => {
    fetchData(filter, limit);
  };

  const LoadingSkeleton = () => (
    <TableBody>
      {[...Array(5)].map((_, i) => (
        <TableRow key={i}>
          <TableCell>
            <Box
              sx={{
                height: 20,
                width: '40px',
                backgroundColor: 'rgba(0, 0, 0, 0.11)',
                borderRadius: 1,
                animation: 'pulse 1.5s ease-in-out infinite',
              }}
            />
          </TableCell>
          <TableCell>
            <Box
              sx={{
                height: 20,
                width: '60%',
                backgroundColor: 'rgba(0, 0, 0, 0.11)',
                borderRadius: 1,
                animation: 'pulse 1.5s ease-in-out infinite',
              }}
            />
          </TableCell>
          <TableCell>
            <Box
              sx={{
                height: 20,
                width: '30%',
                backgroundColor: 'rgba(0, 0, 0, 0.11)',
                borderRadius: 1,
                animation: 'pulse 1.5s ease-in-out infinite',
              }}
            />
          </TableCell>
          <TableCell>
            <Box
              sx={{
                height: 20,
                width: '80px',
                backgroundColor: 'rgba(0, 0, 0, 0.11)',
                borderRadius: 1,
                animation: 'pulse 1.5s ease-in-out infinite',
              }}
            />
          </TableCell>
          <TableCell>
            <Box
              sx={{
                height: 20,
                width: '80px',
                backgroundColor: 'rgba(0, 0, 0, 0.11)',
                borderRadius: 1,
                animation: 'pulse 1.5s ease-in-out infinite',
              }}
            />
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  );

  return (
    <Box
      sx={{
        minHeight: '100vh',
        backgroundColor: theme.palette.grey[100],
        p: 3,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'flex-start',
      }}
    >
      <Card
        elevation={4}
        sx={{
          width: '100%',
          maxWidth: 1400,
          borderRadius: 2,
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <Box
          sx={{
            p: 2,
            backgroundColor: theme.palette.primary.main,
            color: 'white',
          }}
        >
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            mb: 2
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <MailIcon />
              <Typography variant="h6" component="h1">
                Email Inbox
              </Typography>
            </Box>
            <Button
              variant="contained"
              color="inherit"
              size="small"
              startIcon={loading ? <CircularProgress size={20} color="primary" /> : <RefreshIcon />}
              onClick={handleRefresh}
              disabled={loading}
              sx={{ 
                bgcolor: 'rgba(255, 255, 255, 0.9)', 
                color: theme.palette.primary.main,
                '&.Mui-disabled': {
                  bgcolor: 'rgba(255, 255, 255, 0.5)',
                }
              }}
            >
              Refresh
            </Button>
          </Box>

          {/* Filters Stack */}
          <Stack direction="row" spacing={1}>
            {/* Filter Select */}
            <FormControl 
              sx={{ 
                flex: 1,
                backgroundColor: 'white',
                borderRadius: 1,
                '& .MuiOutlinedInput-root': {
                  '& fieldset': {
                    borderColor: 'transparent',
                  },
                }
              }}
              size="small"
            >
              <Select
                value={filter}
                onChange={handleFilterChange}
                displayEmpty
                disabled={loading}
                startAdornment={
                  <FilterIcon sx={{ mr: 1, color: theme.palette.primary.main }} />
                }
              >
                <MenuItem value="ALL">All Emails</MenuItem>
                <MenuItem value="ATS">ATS</MenuItem>
                <MenuItem value="TMO">TMO</MenuItem>
              </Select>
            </FormControl>

            {/* Limit Select */}
            {/* <FormControl 
              sx={{ 
                flex: 1,
                backgroundColor: 'white',
                borderRadius: 1,
                '& .MuiOutlinedInput-root': {
                  '& fieldset': {
                    borderColor: 'transparent',
                  },
                }
              }}
              size="small"
            >
              <Select
                value={limit}
                onChange={handleLimitChange}
                displayEmpty
                disabled={loading}
                startAdornment={
                  <ListIcon sx={{ mr: 1, color: theme.palette.primary.main }} />
                }
              >
                <MenuItem value={10}>10 Emails</MenuItem>
                <MenuItem value={50}>50 Emails</MenuItem>
                <MenuItem value={100}>100 Emails</MenuItem>
                <MenuItem value={200}>200 Emails</MenuItem>
              </Select>
            </FormControl> */}
          </Stack>
        </Box>

        <Box sx={{ p: 0 }}>
          {/* Error Alert */}
          {error && (
            <Alert 
              severity="error" 
              icon={<ErrorIcon />}
              sx={{ m: 2 }}
            >
              {error}
            </Alert>
          )}

          {/* Email Count */}
          <Typography
            variant="subtitle2"
            sx={{
              px: 2,
              py: 1,
              backgroundColor: theme.palette.grey[100],
              borderBottom: `1px solid ${theme.palette.divider}`
            }}
          >
            {data.length} {data.length === 1 ? 'email' : 'emails'} found
          </Typography>

          {/* Table Container */}
          <TableContainer sx={{ maxHeight: 600 }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ width: '80px', fontWeight: 'bold' }}>Sr No</TableCell>
                  <TableCell sx={{ width: '80px', fontWeight: 'bold' }}>From</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Subject</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Date</TableCell>
                  <TableCell sx={{ width: '100px', fontWeight: 'bold' }}>Urgent</TableCell>
                  <TableCell sx={{ width: '120px', fontWeight: 'bold' }}>SKU</TableCell>
                </TableRow>
              </TableHead>
              
              {loading ? (
                <LoadingSkeleton />
              ) : (
                <TableBody>
                  {data.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={4} align="center">
                        <Typography sx={{ py: 2, color: theme.palette.text.secondary }}>
                          No emails found for the selected filter
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    data.map((email, index) => (
                      <TableRow
                        key={index}
                        onClick={() => handleEmailClick(email, index)}
                        sx={{
                          cursor: 'pointer',
                          '&:hover': {
                            backgroundColor: theme.palette.action.hover,
                          },
                        }}
                      >
                        <TableCell>{index + 1}</TableCell>
                        <TableCell>{email.From}</TableCell>
                        <TableCell>{email.subject}</TableCell>
                        <TableCell>{email.date}</TableCell>
                        <TableCell>
                          {email.urgent ? ( // Random urgent status for demonstration
                            <CheckCircleIcon sx={{ color: theme.palette.error.main }} />
                          ) : (
                            <CancelIcon sx={{ color: theme.palette.success.main }} />
                          )}
                        </TableCell>
                        <TableCell>{email.sku ? email.sku : <CancelIcon sx={{ color: theme.palette.success.main }} />}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              )}
            </Table>
          </TableContainer>
        </Box>
      </Card>
    </Box>
  );
}