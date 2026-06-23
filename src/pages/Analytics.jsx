import { 
  BarChart3, CheckCircle, Eye, XCircle, AlertCircle, 
  UserMinus, Search, Filter, Download, ChevronLeft, ChevronRight, Loader2
} from 'lucide-react';
import { motion } from 'framer-motion';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import { useState, useEffect } from 'react';
import { useToast } from '../components/Toast';

const Analytics = () => {
  const { addToast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterCampaign, setFilterCampaign] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [emailLogs, setEmailLogs] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [stats, setStats] = useState({
    delivered: 0,
    opened: 0,
    failed: 0,
    bounced: 0,
    unsubscribed: 0,
    total: 0
  });
  const itemsPerPage = 10;

  useEffect(() => {
    fetchAnalytics();
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      const response = await fetch('http://const API_URL = import.meta.env.VITE_API_URL/api/v1/campaigns/');
      if (response.ok) {
        const data = await response.json();
        console.log('📋 Campaigns Fetched:', data.campaigns?.length || 0, 'campaigns');
        console.log('📋 Campaigns:', data.campaigns);
        setCampaigns(data.campaigns || []);
      }
    } catch (error) {
      console.error('Error fetching campaigns:', error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      
      // Fetch analytics stats
      const statsResponse = await fetch('http://const API_URL = import.meta.env.VITE_API_URL/api/v1/analytics/stats');
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats({
          delivered: statsData.delivered || 0,
          opened: statsData.opened || 0,
          failed: statsData.failed || 0,
          bounced: statsData.bounced || 0,
          unsubscribed: statsData.unsubscribed || 0,
          total: statsData.total_sent || 0
        });
      }
      
      // Fetch email logs
      const logsResponse = await fetch('http://const API_URL = import.meta.env.VITE_API_URL/api/v1/analytics/email-logs?limit=1000');
      if (logsResponse.ok) {
        const logsData = await logsResponse.json();
        console.log('📧 Email Logs Fetched:', logsData.email_logs?.length || 0, 'emails');
        console.log('📧 First log sample:', logsData.email_logs?.[0]);
        setEmailLogs(logsData.email_logs || []);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setLoading(false);
      setTimeout(() => {
        addToast('Failed to fetch analytics', 'error');
      }, 0);
    }
  };

  // Analytics Summary Data
  const analyticsData = [
    {
      title: 'Delivered',
      value: stats.delivered.toLocaleString(),
      percentage: stats.total > 0 ? ((stats.delivered / stats.total) * 100).toFixed(1) : 0,
      icon: CheckCircle,
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-500/10',
      textColor: 'text-green-500',
      trend: stats.delivered > 0 ? '+100%' : '0%'
    },
    {
      title: 'Opened',
      value: stats.opened.toLocaleString(),
      percentage: stats.total > 0 ? ((stats.opened / stats.total) * 100).toFixed(1) : 0,
      icon: Eye,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-500/10',
      textColor: 'text-blue-500',
      trend: stats.opened > 0 ? '+100%' : '0%'
    },
    {
      title: 'Failed',
      value: stats.failed.toLocaleString(),
      percentage: stats.total > 0 ? ((stats.failed / stats.total) * 100).toFixed(1) : 0,
      icon: XCircle,
      color: 'from-red-500 to-red-600',
      bgColor: 'bg-red-500/10',
      textColor: 'text-red-500',
      trend: stats.failed > 0 ? '+100%' : '0%'
    },
    {
      title: 'Bounced',
      value: stats.bounced.toLocaleString(),
      percentage: stats.total > 0 ? ((stats.bounced / stats.total) * 100).toFixed(1) : 0,
      icon: AlertCircle,
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-500/10',
      textColor: 'text-orange-500',
      trend: stats.bounced > 0 ? '+100%' : '0%'
    },
    {
      title: 'Unsubscribed',
      value: stats.unsubscribed.toLocaleString(),
      percentage: stats.total > 0 ? ((stats.unsubscribed / stats.total) * 100).toFixed(1) : 0,
      icon: UserMinus,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-500/10',
      textColor: 'text-purple-500',
      trend: stats.unsubscribed > 0 ? '+100%' : '0%'
    }
  ];

  // Filter and search
  const filteredRecipients = emailLogs.filter(log => {
    const matchesSearch = log.recipient_email.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          (log.campaign_name && log.campaign_name.toLowerCase().includes(searchQuery.toLowerCase()));
    
    // Campaign filter - ensure both sides are compared correctly
    const matchesCampaign = filterCampaign === 'all' || String(log.campaign_id) === String(filterCampaign);
    
    // Status filter
    let matchesStatus = true;
    if (filterStatus !== 'all') {
      if (filterStatus === 'delivered') matchesStatus = log.delivery_status === 'delivered';
      else if (filterStatus === 'opened') matchesStatus = log.opened === true;
      else if (filterStatus === 'bounced') matchesStatus = log.bounced === true;
      else if (filterStatus === 'failed') matchesStatus = log.delivery_status === 'failed';
    }
    
    return matchesSearch && matchesCampaign && matchesStatus;
  });

  // Debug logging
  console.log('🔍 Filter State:', {
    filterCampaign,
    filterStatus,
    searchQuery,
    totalLogs: emailLogs.length,
    filteredCount: filteredRecipients.length
  });

  // Pagination
  const totalPages = Math.ceil(filteredRecipients.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentRecipients = filteredRecipients.slice(startIndex, endIndex);

  const handleExport = async () => {
    try {
      setExporting(true);
      
      // Build export URL with filters
      const params = new URLSearchParams();
      params.append('format', 'csv');
      
      if (filterStatus !== 'all') {
        params.append('status', filterStatus);
      }
      
      if (searchQuery) {
        params.append('search', searchQuery);
      }
      
      // Call export API
      const response = await fetch(`http://const API_URL = import.meta.env.VITE_API_URL/api/v1/exports/email-logs?${params.toString()}`);
      
      if (response.ok) {
        // Get filename from response headers or use default
        const contentDisposition = response.headers.get('content-disposition');
        let filename = 'email_analytics_export.csv';
        
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
          if (filenameMatch) {
            filename = filenameMatch[1];
          }
        }
        
        // Download file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        setTimeout(() => {
          addToast('Export successful! Check your downloads folder', 'success');
        }, 0);
      } else {
        throw new Error('Export failed');
      }
    } catch (error) {
      console.error('Export error:', error);
      setTimeout(() => {
        addToast('Export failed. Please try again.', 'error');
      }, 0);
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 text-gold animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center shadow-xl">
            <BarChart3 className="w-9 h-9 text-white" />
          </div>
          <div>
            <h2 className="text-4xl font-black text-gray-900">Email Analytics</h2>
            <p className="text-lg font-bold text-gray-700">Track and analyze email performance</p>
          </div>
        </div>
        <Button icon={Download} onClick={handleExport} disabled={exporting}>
          {exporting ? 'Exporting...' : 'Export Data'}
        </Button>
      </motion.div>

      {/* Analytics Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {analyticsData.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card hover className="h-full">
              <div className="flex items-start justify-between mb-3">
                <div className={`${stat.bgColor} p-4 rounded-xl shadow-md`}>
                  <stat.icon className={`w-7 h-7 ${stat.textColor}`} />
                </div>
                <span className="text-xs font-bold text-green-600">{stat.trend}</span>
              </div>
              <p className="text-gray-700 text-base font-bold mb-1">{stat.title}</p>
              <h3 className="text-3xl font-black text-gray-900 mb-1">{stat.value}</h3>
              <p className="text-sm font-semibold text-gray-600">{stat.percentage}% of total</p>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Data Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
            <div>
              <h3 className="text-2xl font-black text-gray-900 mb-1">Email Activity</h3>
              <p className="text-base font-bold text-gray-700">
                Showing {startIndex + 1} to {Math.min(endIndex, filteredRecipients.length)} of {filteredRecipients.length} entries
              </p>
            </div>

            <div className="flex gap-3 w-full sm:w-auto flex-wrap">
              <div className="relative flex-1 sm:flex-initial">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-6 h-6 text-gray-500" />
                <Input
                  placeholder="Search emails..."
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setCurrentPage(1); // Reset to first page on search
                  }}
                  className="pl-11 w-full sm:w-64 font-semibold"
                />
              </div>

              <div className="relative">
                <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-6 h-6 text-gold pointer-events-none" />
                <select
                  value={filterCampaign}
                  onChange={(e) => {
                    setFilterCampaign(e.target.value);
                    setCurrentPage(1); // Reset to first page on filter
                  }}
                  className="pl-11 pr-4 py-2.5 bg-gradient-to-r from-gold/10 to-gold-light/10 border-2 border-gold/30 rounded-xl text-gray-900 font-black focus:outline-none focus:border-gold appearance-none cursor-pointer shadow-sm hover:shadow-md transition-all min-w-[200px]"
                >
                  <option value="all">All Campaigns</option>
                  {campaigns.map(campaign => (
                    <option key={campaign.id} value={campaign.id}>
                      {campaign.campaign_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="relative">
                <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-6 h-6 text-gray-500 pointer-events-none" />
                <select
                  value={filterStatus}
                  onChange={(e) => {
                    setFilterStatus(e.target.value);
                    setCurrentPage(1); // Reset to first page on filter
                  }}
                  className="pl-11 pr-4 py-2.5 bg-gray-50 border-2 border-gray-300 rounded-xl text-gray-900 font-bold focus:outline-none focus:border-gold appearance-none cursor-pointer shadow-sm hover:shadow-md transition-all"
                >
                  <option value="all">All Status</option>
                  <option value="delivered">Delivered</option>
                  <option value="opened">Opened</option>
                  <option value="bounced">Bounced</option>
                  <option value="failed">Failed</option>
                </select>
              </div>
            </div>
          </div>

          {currentRecipients.length === 0 ? (
            <div className="text-center py-12">
              <BarChart3 className="w-20 h-20 text-gray-400 mx-auto mb-4" />
              <h3 className="text-2xl font-black text-gray-900 mb-2">No emails found</h3>
              <p className="text-lg font-bold text-gray-600">Send your first campaign to see analytics here</p>
            </div>
          ) : (
            <>
              {/* Table */}
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b-2 border-gray-200 bg-gray-50">
                      <th className="text-left py-4 px-4 text-base font-black text-gray-900">Recipient</th>
                      <th className="text-left py-4 px-4 text-base font-black text-gray-900">Subject</th>
                      <th className="text-left py-4 px-4 text-base font-black text-gray-900">Campaign</th>
                      <th className="text-left py-4 px-4 text-base font-black text-gray-900">Status</th>
                      <th className="text-left py-4 px-4 text-base font-black text-gray-900">Opened</th>
                      <th className="text-left py-4 px-4 text-base font-black text-gray-900">Sent At</th>
                    </tr>
                  </thead>
                  <tbody>
                    {currentRecipients.map((log, index) => (
                      <motion.tr
                        key={log.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="border-b border-gray-200 hover:bg-gray-50 transition-colors"
                      >
                        <td className="py-4 px-4">
                          <p className="text-gray-900 font-black text-sm">{log.recipient_email}</p>
                        </td>
                        <td className="py-4 px-4">
                          <p className="text-gray-800 font-bold text-sm">{log.subject}</p>
                        </td>
                        <td className="py-4 px-4">
                          <p className="text-gray-700 font-bold text-sm">{log.campaign_name}</p>
                        </td>
                        <td className="py-4 px-4">
                          <span className={`px-3 py-1.5 rounded-full text-xs font-black ${
                            log.delivery_status === 'delivered' ? 'bg-green-100 text-green-700' :
                            log.delivery_status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                            log.delivery_status === 'failed' ? 'bg-red-100 text-red-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>
                            {log.delivery_status}
                          </span>
                        </td>
                        <td className="py-4 px-4">
                          {log.opened ? (
                            <Eye className="w-6 h-6 text-blue-600" />
                          ) : (
                            <div className="w-6 h-6 rounded-full border-2 border-gray-400" />
                          )}
                        </td>
                        <td className="py-4 px-4 text-gray-700 font-bold text-sm">
                          {new Date(log.sent_at).toLocaleString()}
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between mt-6 pt-6 border-t-2 border-gray-200">
                  <p className="text-sm font-bold text-gray-700">
                    Page {currentPage} of {totalPages}
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                      disabled={currentPage === 1}
                    >
                      <ChevronLeft className="w-5 h-5" />
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                      disabled={currentPage === totalPages}
                    >
                      <ChevronRight className="w-5 h-5" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </Card>
      </motion.div>
    </div>
  );
};

export default Analytics;
