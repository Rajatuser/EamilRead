import * as React from 'react';
import axios from 'axios';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Divider,
  CircularProgress,
  Alert,
  useTheme,
  Paper,
  IconButton,
  Tooltip,
  Chip,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  AccessTime as AccessTimeIcon,
  Person as PersonIcon,
  Email as EmailIcon,
} from '@mui/icons-material';

export default function EmailDetails({ emailId, onBack }) {
  const [emailData, setEmailData] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);
  const theme = useTheme();

  React.useEffect(() => {
    const fetchEmailDetails = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.get(`http://192.168.0.129:8000/email/${emailId}`);
        setEmailData(response.data);
      } catch (err) {
        console.error(err);
        setError('Unable to fetch email details. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    if (emailId) {
      fetchEmailDetails();
    }
  }, [emailId]);

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch (e) {
      return dateString;
    }
  };

  const extractEmailAddress = (emailString) => {
    const matches = emailString?.match(/<(.+?)>/);
    return matches ? matches[1] : emailString;
  };

  const extractDisplayName = (emailString) => {
    const matches = emailString?.match(/^"?([^"<]+)"?/);
    return matches ? matches[1].trim() : emailString;
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '400px',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert 
        severity="error" 
        sx={{ m: 2 }}
        action={
          <IconButton
            color="inherit"
            size="small"
            onClick={onBack}
          >
            <ArrowBackIcon />
          </IconButton>
        }
      >
        {error}
      </Alert>
    );
  }

  if (!emailData) {
    return null;
  }

  return (
    <Card
      elevation={4}
      sx={{
        width: '100%',
        maxWidth: 800,
        margin: 'auto',
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
          display: 'flex',
          alignItems: 'center',
          gap: 2,
        }}
      >
        <Tooltip title="Back to inbox">
          <IconButton 
            onClick={onBack}
            sx={{ color: 'white' }}
          >
            <ArrowBackIcon />
          </IconButton>
        </Tooltip>
        <Typography variant="h6" component="h1">
          Email Details
        </Typography>
      </Box>

      <CardContent>
        {/* Subject */}
        <Typography
          variant="h5"
          gutterBottom
          sx={{
            fontWeight: 500,
            wordBreak: 'break-word',
          }}
        >
          {emailData.subject}
        </Typography>

        {/* Metadata Paper */}
        <Paper
          variant="outlined"
          sx={{
            p: 2,
            mb: 3,
            backgroundColor: theme.palette.grey[50],
          }}
        >
          {/* From */}
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5, gap: 1 }}>
            <PersonIcon color="action" />
            <Box>
              <Typography variant="subtitle2" color="text.secondary">
                From:
              </Typography>
              <Typography>
                {extractDisplayName(emailData.from)}
                <Typography
                  component="span"
                  color="text.secondary"
                  sx={{ ml: 1 }}
                >
                  ({extractEmailAddress(emailData.from)})
                </Typography>
              </Typography>
            </Box>
          </Box>

          {/* To */}
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5, gap: 1 }}>
            <EmailIcon color="action" />
            <Box>
              <Typography variant="subtitle2" color="text.secondary">
                To:
              </Typography>
              <Typography>
                {extractDisplayName(emailData.to)}
                <Typography
                  component="span"
                  color="text.secondary"
                  sx={{ ml: 1 }}
                >
                  ({extractEmailAddress(emailData.to)})
                </Typography>
              </Typography>
            </Box>
          </Box>

          {/* Date */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AccessTimeIcon color="action" />
            <Box>
              <Typography variant="subtitle2" color="text.secondary">
                Date:
              </Typography>
              <Typography>{formatDate(emailData.date)}</Typography>
            </Box>
          </Box>
        </Paper>

        <Divider sx={{ my: 2 }} />

        {/* Email Body */}
        <Paper
          variant="outlined"
          sx={{
            p: 3,
            backgroundColor: 'white',
            '& pre': {
              whiteSpace: 'pre-wrap',
              wordWrap: 'break-word',
              fontFamily: 'inherit',
              margin: 0,
            },
          }}
        >
          <pre>{emailData.body}</pre>
        </Paper>
      </CardContent>
    </Card>
  );
}