import * as React from 'react';
import axios from 'axios';
import { 
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Divider,
  Avatar,
  CircularProgress,
  Alert,
  Fade,
  useTheme,
  FormControl,
  Select,
  MenuItem,
  Stack
} from '@mui/material';
import { 
  Refresh as RefreshIcon,
  Mail as MailIcon,
  ErrorOutline as ErrorIcon,
  FilterList as FilterIcon,
  FormatListNumbered as ListIcon
} from '@mui/icons-material';

export default function EmailReader() {
  const [data, setData] = React.useState([]);
  const [error, setError] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [filter, setFilter] = React.useState('ALL');
  const [limit, setLimit] = React.useState(100);
  const theme = useTheme();

  const fetchData = async (keyword = 'all', emailLimit = limit) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        `http://192.168.0.129:8000/emails/${keyword.toLowerCase()}?limit=${emailLimit}`
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
    <Box sx={{ p: 2 }}>
      {[...Array(5)].map((_, i) => (
        <Box
          key={i}
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            mb: 2,
            animation: 'pulse 1.5s ease-in-out infinite',
            '@keyframes pulse': {
              '0%, 100%': { opacity: 1 },
              '50%': { opacity: 0.5 },
            },
          }}
        >
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: '50%',
              backgroundColor: 'rgba(0, 0, 0, 0.11)',
            }}
          />
          <Box sx={{ flex: 1 }}>
            <Box
              sx={{
                height: 12,
                width: '70%',
                backgroundColor: 'rgba(0, 0, 0, 0.11)',
                borderRadius: 1,
                mb: 1,
              }}
            />
            <Box
              sx={{
                height: 8,
                width: '40%',
                backgroundColor: 'rgba(0, 0, 0, 0.11)',
                borderRadius: 1,
              }}
            />
          </Box>
        </Box>
      ))}
    </Box>
  );

  return (
    <Box
      sx={{
        minHeight: '100vh',
        backgroundColor: theme.palette.grey[100],
        p: 3,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <Card
        elevation={4}
        sx={{
          width: '100%',
          maxWidth: 600,
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
          <Stack spacing={2}>
            {/* Filter Select */}
            <FormControl 
              fullWidth
              size="small"
              sx={{ 
                backgroundColor: 'white',
                borderRadius: 1,
                '& .MuiOutlinedInput-root': {
                  '& fieldset': {
                    borderColor: 'transparent',
                  },
                  '&:hover fieldset': {
                    borderColor: 'transparent',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: 'transparent',
                  },
                  '&.Mui-disabled': {
                    backgroundColor: 'rgba(255, 255, 255, 0.7)',
                  }
                },
              }}
            >
              <Select
                value={filter}
                onChange={handleFilterChange}
                displayEmpty
                disabled={loading}
                startAdornment={
                  <FilterIcon 
                    sx={{ 
                      mr: 1, 
                      color: loading ? theme.palette.action.disabled : theme.palette.primary.main 
                    }} 
                  />
                }
              >
                <MenuItem value="ALL">All Emails</MenuItem>
                <MenuItem value="ATS">ATS</MenuItem>
                <MenuItem value="TMO">TMO</MenuItem>
              </Select>
            </FormControl>

            {/* Limit Select */}
            <FormControl 
              fullWidth
              size="small"
              sx={{ 
                backgroundColor: 'white',
                borderRadius: 1,
                '& .MuiOutlinedInput-root': {
                  '& fieldset': {
                    borderColor: 'transparent',
                  },
                  '&:hover fieldset': {
                    borderColor: 'transparent',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: 'transparent',
                  },
                  '&.Mui-disabled': {
                    backgroundColor: 'rgba(255, 255, 255, 0.7)',
                  }
                },
              }}
            >
              <Select
                value={limit}
                onChange={handleLimitChange}
                displayEmpty
                disabled={loading}
                startAdornment={
                  <ListIcon 
                    sx={{ 
                      mr: 1, 
                      color: loading ? theme.palette.action.disabled : theme.palette.primary.main 
                    }} 
                  />
                }
              >
                <MenuItem value={10}>10 Emails</MenuItem>
                <MenuItem value={50}>50 Emails</MenuItem>
                <MenuItem value={100}>100 Emails</MenuItem>
                <MenuItem value={200}>200 Emails</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </Box>

        <CardContent sx={{ p: 0 }}>
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

          {/* Loading State */}
          {loading ? (
            <LoadingSkeleton />
          ) : (
            /* Email List */
            <Box sx={{ maxHeight: 600, overflow: 'auto' }}>
              {data.length === 0 ? (
                <Typography sx={{ p: 3, textAlign: 'center', color: theme.palette.text.secondary }}>
                  No emails found for the selected filter
                </Typography>
              ) : (
                data.map((email, index) => (
                  <Fade in key={index}>
                    <Box>
                      <Box
                        onClick={() => handleEmailClick(email, index)}
                        sx={{
                          p: 2,
                          display: 'flex',
                          alignItems: 'center',
                          gap: 2,
                          cursor: 'pointer',
                          transition: 'all 0.2s ease',
                          '&:hover': {
                            backgroundColor: theme.palette.action.hover,
                          },
                        }}
                      >
                        <Avatar
                          sx={{
                            bgcolor: theme.palette.primary.main,
                            width: 40,
                            height: 40,
                          }}
                        >
                          {email.subject.charAt(0).toUpperCase()}
                        </Avatar>
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                          <Typography
                            variant="subtitle1"
                            sx={{
                              fontWeight: 500,
                              mb: 0.5,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                            }}
                          >
                            {email.subject}
                          </Typography>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                            }}
                          >
                            {new Date().toLocaleDateString()}
                          </Typography>
                        </Box>
                      </Box>
                      <Divider />
                    </Box>
                  </Fade>
                ))
              )}
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}