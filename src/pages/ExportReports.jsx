import { 
  FileDown, Calendar, CheckCircle, Eye, AlertCircle, 
  UserMinus, FileSpreadsheet, FileText, Download, Filter, Loader2
} from 'lucide-react';
import { motion } from 'framer-motion';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import { useState, useEffect } from 'react';
import { useToast } from '../components/Toast';

const ExportReports = () => {
  const { addToast } = useToast();
  const [dateRange, setDateRange] = useState({
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0]
  });
  const [selectedCampaign, setSelectedCampaign] = useState('all');
  const [exporting, setExporting] = useState(null);
  const [loading, setLoading] = useState(true);
  const [campaigns, setCampaigns] = useState([]);
  const [stats, setStats] = useState({
    delivered: 0,
    opened: 0,
    bounced: 0,
    unsubscribed: 0,
    total: 0
  });

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/campaigns/');
      if (response.ok) {
        const data = await response.json();
        
        const campaignList = [{ id: 'all', name: 'All Campaigns' }];
        let delivered = 0, opened = 0, bounced = 0, unsubscribed = 0, total = 0;
        
        if (data.campaigns) {
          data.campaigns.forEach(campaign => {
            campaignList.push({
              id: campaign.id,
              name: campaign.campaign_name
            });
            
            delivered += campaign.delivered_count || 0;
            opened += campaign.opened_count || 0;
            bounced += campaign.bounced_count || 0;
            unsubscribed += campaign.unsubscribed_count || 0;
            total += campaign.sent_count || 0;
          });
        }
        
        setCampaigns(campaignList);
        setStats({ delivered, opened, bounced, unsubscribed, total });
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching campaigns:', error);
      setLoading(false);
    }
  };

  // Export categories with real stats
  const exportCategories = [
    {
      id: 'delivered',
      title: 'Delivered Emails',
      description: 'Export all successfully delivered emails',
      count: stats.delivered.toLocaleString(),
      percentage: stats.total > 0 ? `${((stats.delivered / stats.total) * 100).toFixed(1)}%` : '0%',
      icon: CheckCircle,
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-500/10',
      textColor: 'text-green-500'
    },
    {
      id: 'opened',
      title: 'Opened Emails',
      description: 'Export emails that were opened by recipients',
      count: stats.opened.toLocaleString(),
      percentage: stats.total > 0 ? `${((stats.opened / stats.total) * 100).toFixed(1)}%` : '0%',
      icon: Eye,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-500/10',
      textColor: 'text-blue-500'
    },
    {
      id: 'bounced',
      title: 'Bounced Emails',
      description: 'Export emails that bounced back',
      count: stats.bounced.toLocaleString(),
      percentage: stats.total > 0 ? `${((stats.bounced / stats.total) * 100).toFixed(1)}%` : '0%',
      icon: AlertCircle,
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-500/10',
      textColor: 'text-orange-500'
    },
    {
      id: 'unsubscribed',
      title: 'Unsubscribed Emails',
      description: 'Export contacts who unsubscribed',
      count: stats.unsubscribed.toLocaleString(),
      percentage: stats.total > 0 ? `${((stats.unsubscribed / stats.total) * 100).toFixed(1)}%` : '0%',
      icon: UserMinus,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-500/10',
      textColor: 'text-purple-500'
    }
  ];

  // Handle export
  const handleExport = async (category, format) => {
    setExporting(`${category}-${format}`);
    
    try {
      // Build query params
      const params = new URLSearchParams({
        format: format,
        start_date: dateRange.startDate,
        end_date: dateRange.endDate
      });
      
      if (selectedCampaign !== 'all') {
        params.append('campaign_id', selectedCampaign);
      }
      
      // Call export API (note: this will download the file)
      const response = await fetch(
        `http://localhost:8000/api/v1/exports/${category}?${params}`,
        { method: 'GET' }
      );
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${category}_export_${dateRange.startDate}_to_${dateRange.endDate}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        setTimeout(() => {
          addToast(`${category} exported successfully as ${format.toUpperCase()}!`, 'success');
        }, 0);
      } else {
        throw new Error('Export failed');
      }
    } catch (error) {
      console.error('Export error:', error);
      setTimeout(() => {
        addToast(`Failed to export ${category}`, 'error');
      }, 0);
    } finally {
      setExporting(null);
    }
  };

  // Quick date presets
  const datePresets = [
    { label: 'Last 7 Days', days: 7 },
    { label: 'Last 30 Days', days: 30 },
    { label: 'Last 90 Days', days: 90 },
    { label: 'This Year', days: 365 }
  ];

  const applyDatePreset = (days) => {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    
    setDateRange({
      startDate: startDate.toISOString().split('T')[0],
      endDate: endDate.toISOString().split('T')[0]
    });
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
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-gold to-gold-light flex items-center justify-center shadow-xl">
            <FileDown className="w-9 h-9 text-white" />
          </div>
          <div>
            <h2 className="text-4xl font-black text-gray-900">Export Reports</h2>
            <p className="text-lg font-bold text-gray-700">Download your email campaign data</p>
          </div>
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card>
          <h3 className="text-2xl font-black text-gray-900 mb-6">Export Filters</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Date Range */}
            <div className="space-y-4">
              <label className="block text-base font-bold text-gray-700">
                <Calendar className="w-6 h-6 inline mr-2" />
                Date Range
              </label>
              <div className="grid grid-cols-2 gap-3">
                <Input
                  type="date"
                  label="Start Date"
                  value={dateRange.startDate}
                  onChange={(e) => setDateRange({ ...dateRange, startDate: e.target.value })}
                />
                <Input
                  type="date"
                  label="End Date"
                  value={dateRange.endDate}
                  onChange={(e) => setDateRange({ ...dateRange, endDate: e.target.value })}
                />
              </div>
              
              {/* Quick Presets */}
              <div className="flex flex-wrap gap-2">
                {datePresets.map(preset => (
                  <button
                    key={preset.label}
                    onClick={() => applyDatePreset(preset.days)}
                    className="px-4 py-2 text-sm font-bold rounded-xl bg-gray-100 border-2 border-gray-300 text-gray-900 hover:border-gold hover:bg-gold/10 transition-all shadow-sm hover:shadow-md"
                  >
                    {preset.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Campaign Selection */}
            <div>
              <label className="block text-base font-bold text-gray-700 mb-3">
                <Filter className="w-6 h-6 inline mr-2" />
                Campaign Filter
              </label>
              <select
                value={selectedCampaign}
                onChange={(e) => setSelectedCampaign(e.target.value)}
                className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-300 rounded-xl text-gray-900 font-bold focus:outline-none focus:border-gold shadow-sm"
              >
                {campaigns.map(campaign => (
                  <option key={campaign.id} value={campaign.id}>
                    {campaign.name}
                  </option>
                ))}
              </select>
              <p className="text-sm font-semibold text-gray-600 mt-2">
                Select a specific campaign or export all campaigns
              </p>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Export Categories */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {exportCategories.map((category, index) => (
          <motion.div
            key={category.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + index * 0.1 }}
          >
            <Card hover>
              <div className="flex items-start gap-4 mb-4">
                <div className={`${category.bgColor} p-4 rounded-xl flex-shrink-0 shadow-md`}>
                  <category.icon className={`w-8 h-8 ${category.textColor}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-xl font-black text-gray-900 mb-1">
                    {category.title}
                  </h3>
                  <p className="text-sm font-bold text-gray-700 mb-3">
                    {category.description}
                  </p>
                  <div className="flex items-baseline gap-3">
                    <span className="text-3xl font-black text-gray-900">
                      {category.count}
                    </span>
                    <span className={`text-base font-bold ${category.textColor}`}>
                      {category.percentage}
                    </span>
                  </div>
                </div>
              </div>

              {/* Export Buttons */}
              <div className="flex gap-3 mt-4 pt-4 border-t-2 border-gray-200">
                <Button
                  variant="secondary"
                  size="sm"
                  className="flex-1"
                  onClick={() => handleExport(category.id, 'csv')}
                  disabled={exporting === `${category.id}-csv`}
                >
                  {exporting === `${category.id}-csv` ? (
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  ) : (
                    <FileText className="w-5 h-5 mr-2" />
                  )}
                  Export CSV
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  className="flex-1"
                  onClick={() => handleExport(category.id, 'xlsx')}
                  disabled={exporting === `${category.id}-xlsx`}
                >
                  {exporting === `${category.id}-xlsx` ? (
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  ) : (
                    <FileSpreadsheet className="w-5 h-5 mr-2" />
                  )}
                  Export Excel
                </Button>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Bulk Export */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-black text-gray-900 mb-2">Bulk Export</h3>
              <p className="text-base font-bold text-gray-700">
                Export all categories in a single comprehensive report
              </p>
            </div>
            <div className="flex gap-3">
              <Button
                variant="secondary"
                icon={FileText}
                onClick={() => handleExport('all', 'csv')}
                disabled={exporting === 'all-csv'}
              >
                {exporting === 'all-csv' ? 'Exporting...' : 'Export All as CSV'}
              </Button>
              <Button
                variant="primary"
                icon={Download}
                onClick={() => handleExport('all', 'xlsx')}
                disabled={exporting === 'all-xlsx'}
              >
                {exporting === 'all-xlsx' ? 'Exporting...' : 'Export All as Excel'}
              </Button>
            </div>
          </div>
        </Card>
      </motion.div>
    </div>
  );
};

export default ExportReports;
