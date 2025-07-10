/**
 * Main Dashboard Component - Overview of AI Interior Design Assistant
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Avatar,
  Chip,
  LinearProgress,
  IconButton,
  Menu,
  MenuItem,
  Divider,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemSecondaryAction,
} from '@mui/material';
import {
  CameraAlt,
  View3D,
  Palette,
  AutoAwesome,
  TrendingUp,
  Schedule,
  MoreVert,
  Add,
  PhotoCamera,
  Architecture,
  Lightbulb,
  ColorLens,
  Home,
  Analytics,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';

// Custom hooks
import { useProjects } from '../../hooks/useProjects';
import { useRecentScans } from '../../hooks/useRecentScans';
import { useRecommendations } from '../../hooks/useRecommendations';

// Components
import QuickActionCard from './QuickActionCard';
import ProjectCard from './ProjectCard';
import RecentActivityCard from './RecentActivityCard';
import RecommendationCard from './RecommendationCard';
import StatsCard from './StatsCard';

const Dashboard = () => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  
  // Custom hooks for data fetching
  const { data: projects, isLoading: projectsLoading } = useProjects({ limit: 6 });
  const { data: recentScans, isLoading: scansLoading } = useRecentScans({ limit: 5 });
  const { data: recommendations, isLoading: recommendationsLoading } = useRecommendations({ limit: 4 });

  // Mock data for demonstration
  const stats = {
    totalProjects: 12,
    completedScans: 45,
    aiRecommendations: 128,
    hoursDesigning: 24,
  };

  const quickActions = [
    {
      title: 'Scan Room',
      description: 'Upload photos to analyze your space',
      icon: <CameraAlt />,
      color: 'primary',
      action: () => navigate('/scan'),
    },
    {
      title: '3D Visualization',
      description: 'View your room in 3D',
      icon: <View3D />,
      color: 'secondary',
      action: () => navigate('/3d-viewer'),
    },
    {
      title: 'Virtual Staging',
      description: 'Stage your room with AI',
      icon: <AutoAwesome />,
      color: 'success',
      action: () => navigate('/staging'),
    },
    {
      title: 'New Project',
      description: 'Start a new design project',
      icon: <Add />,
      color: 'info',
      action: () => navigate('/projects?action=create'),
    },
  ];

  const recentActivity = [
    {
      id: 1,
      type: 'scan',
      title: 'Living Room Scan Completed',
      description: 'Modern style detected with 85% confidence',
      timestamp: '2 hours ago',
      icon: <PhotoCamera />,
      color: 'primary',
    },
    {
      id: 2,
      type: 'recommendation',
      title: 'New AI Recommendations',
      description: '5 furniture suggestions for your bedroom',
      timestamp: '4 hours ago',
      icon: <Lightbulb />,
      color: 'warning',
    },
    {
      id: 3,
      type: 'project',
      title: 'Project Updated',
      description: 'Kitchen Renovation project saved',
      timestamp: '1 day ago',
      icon: <Architecture />,
      color: 'info',
    },
    {
      id: 4,
      type: 'staging',
      title: 'Virtual Staging Complete',
      description: 'Bedroom staging with modern furniture',
      timestamp: '2 days ago',
      icon: <ColorLens />,
      color: 'secondary',
    },
  ];

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <>
      <Helmet>
        <title>Dashboard - AI Interior Design Assistant</title>
        <meta name="description" content="Your AI-powered interior design dashboard with room scanning, 3D visualization, and smart recommendations." />
      </Helmet>

      <Box sx={{ flexGrow: 1, p: 3 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Typography variant="h3" component="h1" gutterBottom>
              Welcome back! 👋
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
              Transform your spaces with AI-powered interior design insights
            </Typography>
          </motion.div>
        </Box>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <StatsCard
                title="Projects"
                value={stats.totalProjects}
                icon={<Home />}
                color="primary"
                trend="+12%"
              />
            </motion.div>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <StatsCard
                title="Room Scans"
                value={stats.completedScans}
                icon={<CameraAlt />}
                color="secondary"
                trend="+8%"
              />
            </motion.div>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <StatsCard
                title="AI Suggestions"
                value={stats.aiRecommendations}
                icon={<AutoAwesome />}
                color="success"
                trend="+24%"
              />
            </motion.div>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
            >
              <StatsCard
                title="Design Hours"
                value={stats.hoursDesigning}
                icon={<Schedule />}
                color="info"
                trend="+16%"
              />
            </motion.div>
          </Grid>
        </Grid>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 3 }}>
            Quick Actions
          </Typography>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {quickActions.map((action, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <QuickActionCard
                  title={action.title}
                  description={action.description}
                  icon={action.icon}
                  color={action.color}
                  onClick={action.action}
                />
              </Grid>
            ))}
          </Grid>
        </motion.div>

        {/* Main Content Grid */}
        <Grid container spacing={3}>
          {/* Recent Projects */}
          <Grid item xs={12} lg={8}>
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.6 }}
            >
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                    <Typography variant="h6" component="h3">
                      Recent Projects
                    </Typography>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => navigate('/projects')}
                    >
                      View All
                    </Button>
                  </Box>
                  
                  {projectsLoading ? (
                    <Box sx={{ width: '100%' }}>
                      <LinearProgress />
                    </Box>
                  ) : (
                    <Grid container spacing={2}>
                      {projects?.slice(0, 4).map((project, index) => (
                        <Grid item xs={12} sm={6} key={project.id}>
                          <ProjectCard project={project} />
                        </Grid>
                      ))}
                    </Grid>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* Recent Activity */}
          <Grid item xs={12} lg={4}>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.7 }}
            >
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" component="h3">
                      Recent Activity
                    </Typography>
                    <IconButton size="small" onClick={handleMenuClick}>
                      <MoreVert />
                    </IconButton>
                  </Box>
                  
                  <List dense>
                    {recentActivity.map((activity, index) => (
                      <React.Fragment key={activity.id}>
                        <ListItem alignItems="flex-start">
                          <ListItemAvatar>
                            <Avatar sx={{ bgcolor: `${activity.color}.main`, width: 32, height: 32 }}>
                              {activity.icon}
                            </Avatar>
                          </ListItemAvatar>
                          <ListItemText
                            primary={activity.title}
                            secondary={
                              <>
                                <Typography component="span" variant="body2" color="text.primary">
                                  {activity.description}
                                </Typography>
                                <br />
                                <Typography component="span" variant="caption" color="text.secondary">
                                  {activity.timestamp}
                                </Typography>
                              </>
                            }
                          />
                        </ListItem>
                        {index < recentActivity.length - 1 && <Divider variant="inset" component="li" />}
                      </React.Fragment>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* AI Recommendations */}
          <Grid item xs={12}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.8 }}
            >
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                    <Typography variant="h6" component="h3">
                      AI Recommendations
                    </Typography>
                    <Chip
                      label="New"
                      color="primary"
                      size="small"
                      icon={<AutoAwesome />}
                    />
                  </Box>
                  
                  {recommendationsLoading ? (
                    <Box sx={{ width: '100%' }}>
                      <LinearProgress />
                    </Box>
                  ) : (
                    <Grid container spacing={2}>
                      {recommendations?.map((recommendation, index) => (
                        <Grid item xs={12} sm={6} md={3} key={index}>
                          <RecommendationCard recommendation={recommendation} />
                        </Grid>
                      ))}
                    </Grid>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        </Grid>

        {/* Context Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={handleMenuClose}>
            <Analytics sx={{ mr: 1 }} />
            View Analytics
          </MenuItem>
          <MenuItem onClick={handleMenuClose}>
            <TrendingUp sx={{ mr: 1 }} />
            Export Report
          </MenuItem>
        </Menu>
      </Box>
    </>
  );
};

export default Dashboard;

