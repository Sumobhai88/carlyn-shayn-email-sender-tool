import { 
  TrendingUp, TrendingDown, Mail, Send, CheckCircle, Eye, 
  XCircle, UserMinus, Activity, BarChart2, Clock, AlertCircle 
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import Table from '../components/Table';
import { useToast } from '../components/Toast';

const Dashboard = () => {
  const { addToast } = useToast();
  const [stats, setStats] = useState({
    totalCampaigns: 0,
    emailsSent: 0,
    delivered: 0,
    openRate: 0,
    failed: 0,
    unsubscribed: 0
  });
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch dashboard data
  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async (showToast = false) => {
    try {
      setLoading(true);
      
      // First, fix campaign stats
      try {
        const fixRes = await fetch('http://localhost:8000/api/v1/campaigns/fix-stats', {
          method: 'POST'
        });
        const fixData = await fixRes.json();
        console.log('Fix stats result:', fixData);
        
        if (showToast) {
          setTimeout(() => {
            addToast('Stats refreshed successfully', 'success');
          }, 100);
        }
      } catch (error) {
        console.log('Stats fix attempt:', error);
        if (showToast) {
          setTimeout(() => {
            addToast('Failed to refresh stats', 'error');
          }, 100);
        }
      }
      
      // Small delay to ensure database is updated
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // Fetch campaigns
      const campaignsRes = await fetch('http://localhost:8000/api/v1/campaigns/');
      const campaignsData = await campaignsRes.json();
      
      console.log('Campaigns data:', campaignsData);
      
      if (campaignsData.campaigns) {
        setCampaigns(campaignsData.campaigns.slice(0, 5)); // Latest 5
        
        // Calculate stats
        const totalCampaigns = campaignsData.campaigns.length;
        const emailsSent = campaignsData.campaigns.reduce((sum, c) => sum + (c.sent_count || 0), 0);
        const delivered = campaignsData.campaigns.reduce((sum, c) => sum + (c.delivered_count || 0), 0);
        const opened = campaignsData.campaigns.reduce((sum, c) => sum + (c.opened_count || 0), 0);
        const failed = campaignsData.campaigns.reduce((sum, c) => sum + (c.failed_count || 0), 0);
        const unsubscribed = campaignsData.campaigns.reduce((sum, c) => sum + (c.unsubscribed_count || 0), 0);
        
        const openRate = delivered > 0 ? ((opened / delivered) * 100).toFixed(1) : 0;
        
        console.log('Calculated stats:', { totalCampaigns, emailsSent, delivered, opened, failed, unsubscribed, openRate });
        
        setStats({
          totalCampaigns,
          emailsSent,
          delivered,
          openRate,
          failed,
          unsubscribed
        });
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      if (showToast) {
        setTimeout(() => {
          addToast('Failed to fetch dashboard data', 'error');
        }, 100);
      }
      setLoading(false);
    }
  };

  // Top Statistics Data
  const statsData = [
    {
      title: 'Total Campaigns',
      value: loading ? '...' : stats.totalCampaigns.toString(),
      change: stats.totalCampaigns > 0 ? '+100%' : '0%',
      trend: stats.totalCampaigns > 0 ? 'up' : 'neutral',
      icon: Mail,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-500/10'
    },
    {
      title: 'Emails Sent',
      value: loading ? '...' : stats.emailsSent.toLocaleString(),
      change: stats.emailsSent > 0 ? '+100%' : '0%',
      trend: stats.emailsSent > 0 ? 'up' : 'neutral',
      icon: Send,
      color: 'from-gold to-gold-light',
      bgColor: 'bg-gold/10'
    },
    {
      title: 'Delivered',
      value: loading ? '...' : stats.delivered.toLocaleString(),
      change: stats.delivered > 0 ? '+100%' : '0%',
      trend: stats.delivered > 0 ? 'up' : 'neutral',
      icon: CheckCircle,
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-500/10'
    },
    {
      title: 'Open Rate',
      value: loading ? '...' : `${stats.openRate}%`,
      change: stats.openRate > 0 ? '+100%' : '0%',
      trend: stats.openRate > 0 ? 'up' : 'neutral',
      icon: Eye,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-500/10'
    },
    {
      title: 'Failed',
      value: loading ? '...' : stats.failed.toLocaleString(),
      change: stats.failed > 0 ? '+100%' : '0%',
      trend: stats.failed > 0 ? 'down' : 'neutral',
      icon: XCircle,
      color: 'from-red-500 to-red-600',
      bgColor: 'bg-red-500/10'
    },
    {
      title: 'Unsubscribed',
      value: loading ? '...' : stats.unsubscribed.toLocaleString(),
      change: stats.unsubscribed > 0 ? '+100%' : '0%',
      trend: stats.unsubscribed > 0 ? 'down' : 'neutral',
      icon: UserMinus,
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-500/10'
    }
  ];

  // Chart Data - Current month only (remove dummy data)
  const chartData = [
    { 
      month: new Date().toLocaleString('default', { month: 'short' }), 
      campaigns: stats.totalCampaigns, 
      emails: stats.emailsSent 
    }
  ];

  // Recent campaigns table columns
  const campaignColumns = [
    { key: 'campaign_name', label: 'Campaign Name' },
    { key: 'status', label: 'Status' },
    { key: 'sent_count', label: 'Sent' },
    { key: 'delivered_count', label: 'Delivered' },
    { key: 'opened_count', label: 'Opened' },
    { key: 'created_at', label: 'Created' }
  ];

  // Format campaign data for table
  const campaignRows = campaigns.map(campaign => ({
    ...campaign,
    status: (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
        campaign.status === 'completed' ? 'bg-green-500/20 text-green-400' :
        campaign.status === 'active' ? 'bg-blue-500/20 text-blue-400' :
        campaign.status === 'paused' ? 'bg-yellow-500/20 text-yellow-400' :
        'bg-gray-500/20 text-gray-400'
      }`}>
        {campaign.status}
      </span>
    ),
    created_at: new Date(campaign.created_at).toLocaleDateString()
  }));

  // Notifications Data
  const notifications = campaigns.length > 0 ? campaigns.slice(0, 3).map(campaign => ({
    id: campaign.id,
    type: campaign.status === 'completed' ? 'success' : 'info',
    title: campaign.status === 'completed' ? 'Campaign Completed' : 'Campaign Active',
    message: `${campaign.campaign_name} - ${campaign.sent_count} emails sent`,
    time: new Date(campaign.created_at).toLocaleTimeString()
  })) : [
    {
      id: 1,
      type: 'info',
      title: 'Welcome!',
      message: 'Start by creating your first campaign',
      time: 'Just now'
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-4xl font-black text-gray-900 mb-2">Dashboard</h1>
          <p className="text-lg font-semibold text-gray-700">Welcome back! Here's your email campaign overview.</p>
        </div>
        <Button onClick={() => fetchDashboardData(true)} variant="secondary" className="whitespace-nowrap">
          <Activity className="w-5 h-5 mr-2" />
          Refresh Stats
        </Button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {statsData.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card hover className="h-full">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-base font-bold text-gray-700 mb-1">{stat.title}</p>
                  <h3 className="text-4xl font-black text-gray-900 mb-2">{stat.value}</h3>
                  <div className="flex items-center gap-2">
                    {stat.trend === 'up' && <TrendingUp className="w-5 h-5 text-green-600" />}
                    {stat.trend === 'down' && <TrendingDown className="w-5 h-5 text-red-600" />}
                    <span className={`text-sm font-bold ${
                      stat.trend === 'up' ? 'text-green-600' : 
                      stat.trend === 'down' ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      {stat.change}
                    </span>
                    <span className="text-gray-600 text-sm font-semibold">vs last period</span>
                  </div>
                </div>
                <div className={`${stat.bgColor} p-4 rounded-xl shadow-lg`}>
                  <stat.icon className="w-7 h-7" style={{ color: 'inherit' }} />
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Campaign Activity Chart */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-2xl font-black text-gray-900 mb-1">Campaign Activity</h3>
                <p className="text-base font-semibold text-gray-700">Last 6 months overview</p>
              </div>
              <BarChart2 className="w-6 h-6 text-gold" />
            </div>
            
            <div className="space-y-4">
              {chartData.map((data, index) => (
                <div key={data.month} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-700 font-bold">{data.month}</span>
                    <span className="text-gray-900 font-black">{data.campaigns} campaigns</span>
                  </div>
                  <motion.div 
                    className="w-full bg-gray-200 rounded-full h-3 overflow-hidden shadow-inner"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.4 + index * 0.1 }}
                  >
                    <motion.div
                      className="h-full bg-gradient-to-r from-gold to-gold-light rounded-full shadow-md"
                      initial={{ width: 0 }}
                      animate={{ width: `${(data.campaigns / 70) * 100}%` }}
                      transition={{ delay: 0.5 + index * 0.1, duration: 0.6 }}
                    />
                  </motion.div>
                </div>
              ))}
            </div>
          </Card>
        </motion.div>

        {/* Email Performance Overview */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-2xl font-black text-gray-900 mb-1">Email Performance</h3>
                <p className="text-base font-semibold text-gray-700">Current period statistics</p>
              </div>
              <Activity className="w-6 h-6 text-gold" />
            </div>
            
            <div className="space-y-6">
              {/* Delivered */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-600 shadow-md"></div>
                    <span className="text-gray-900 font-bold">Delivered</span>
                  </div>
                  <span className="text-gray-900 font-black">
                    {stats.emailsSent > 0 ? ((stats.delivered / stats.emailsSent) * 100).toFixed(1) : 0}%
                  </span>
                </div>
                <motion.div 
                  className="w-full bg-gray-200 rounded-full h-3 overflow-hidden shadow-inner"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <motion.div
                    className="h-full bg-gradient-to-r from-green-600 to-green-500 rounded-full shadow-md"
                    initial={{ width: 0 }}
                    animate={{ width: stats.emailsSent > 0 ? `${(stats.delivered / stats.emailsSent) * 100}%` : '0%' }}
                    transition={{ delay: 0.6, duration: 0.8 }}
                  />
                </motion.div>
              </div>

              {/* Failed */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-600 shadow-md"></div>
                    <span className="text-gray-900 font-bold">Failed</span>
                  </div>
                  <span className="text-gray-900 font-black">
                    {stats.emailsSent > 0 ? ((stats.failed / stats.emailsSent) * 100).toFixed(1) : 0}%
                  </span>
                </div>
                <motion.div 
                  className="w-full bg-gray-200 rounded-full h-3 overflow-hidden shadow-inner"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <motion.div
                    className="h-full bg-gradient-to-r from-red-600 to-red-500 rounded-full shadow-md"
                    initial={{ width: 0 }}
                    animate={{ width: stats.emailsSent > 0 ? `${(stats.failed / stats.emailsSent) * 100}%` : '0%' }}
                    transition={{ delay: 0.7, duration: 0.8 }}
                  />
                </motion.div>
              </div>

              {/* Pending */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-yellow-600 shadow-md"></div>
                    <span className="text-gray-900 font-bold">Pending</span>
                  </div>
                  <span className="text-gray-900 font-black">
                    {stats.emailsSent > 0 
                      ? (((stats.emailsSent - stats.delivered - stats.failed) / stats.emailsSent) * 100).toFixed(1) 
                      : 0}%
                  </span>
                </div>
                <motion.div 
                  className="w-full bg-gray-200 rounded-full h-3 overflow-hidden shadow-inner"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <motion.div
                    className="h-full bg-gradient-to-r from-yellow-600 to-yellow-500 rounded-full shadow-md"
                    initial={{ width: 0 }}
                    animate={{ 
                      width: stats.emailsSent > 0 
                        ? `${((stats.emailsSent - stats.delivered - stats.failed) / stats.emailsSent) * 100}%` 
                        : '0%' 
                    }}
                    transition={{ delay: 0.8, duration: 0.8 }}
                  />
                </motion.div>
              </div>
            </div>
          </Card>
        </motion.div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Campaigns */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="lg:col-span-2"
        >
          <Card>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-2xl font-black text-gray-900 mb-1">Recent Campaigns</h3>
                <p className="text-base font-semibold text-gray-700">Your latest email campaigns</p>
              </div>
              <Clock className="w-6 h-6 text-gold" />
            </div>
            
            {campaignRows.length > 0 ? (
              <Table 
                columns={campaignColumns} 
                data={campaignRows}
              />
            ) : (
              <div className="text-center py-8">
                <Mail className="w-16 h-16 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-900 font-bold text-lg">No campaigns yet</p>
                <p className="text-base font-semibold text-gray-600 mt-1">Create your first campaign to get started</p>
              </div>
            )}
          </Card>
        </motion.div>

        {/* Recent Notifications */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-2xl font-black text-gray-900 mb-1">Recent Activity</h3>
                <p className="text-base font-semibold text-gray-700">Latest notifications</p>
              </div>
              <AlertCircle className="w-6 h-6 text-gold" />
            </div>
            
            <div className="space-y-4">
              {notifications.map((notification) => (
                <div 
                  key={notification.id}
                  className="p-4 rounded-xl bg-gray-50 border-2 border-gray-200 hover:border-gold/40 hover:shadow-lg transition-all cursor-pointer"
                >
                  <div className="flex items-start gap-3">
                    <div className={`p-3 rounded-xl shadow-md ${
                      notification.type === 'success' ? 'bg-green-100' :
                      notification.type === 'warning' ? 'bg-yellow-100' :
                      notification.type === 'error' ? 'bg-red-100' :
                      'bg-blue-100'
                    }`}>
                      {notification.type === 'success' && <CheckCircle className="w-5 h-5 text-green-600" />}
                      {notification.type === 'warning' && <AlertCircle className="w-5 h-5 text-yellow-600" />}
                      {notification.type === 'error' && <XCircle className="w-5 h-5 text-red-600" />}
                      {notification.type === 'info' && <Activity className="w-5 h-5 text-blue-600" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-black text-gray-900 mb-1">{notification.title}</p>
                      <p className="text-xs font-bold text-gray-700 truncate">{notification.message}</p>
                      <p className="text-xs font-semibold text-gray-500 mt-1">{notification.time}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default Dashboard;
