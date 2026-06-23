import { 
  Zap, Send, Upload as UploadIcon, X, FileText, 
  Play, Pause, Square, Check, Clock, XCircle, Mail,
  Eye, Code, User, Activity, CheckCircle
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import Textarea from '../components/Textarea';
import RichTextEditor from '../components/RichTextEditor';
import { useState, useRef, useEffect } from 'react';
import { useToast } from '../components/Toast';

const CampaignBuilder = () => {
  const [campaignName, setCampaignName] = useState('');
  const [subjectLine, setSubjectLine] = useState('');
  const [emailBody, setEmailBody] = useState('');
  const [file, setFile] = useState(null);
  const [manualEmails, setManualEmails] = useState('');
  const [uploadMode, setUploadMode] = useState('csv'); // 'csv' or 'manual'
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [campaignStatus, setCampaignStatus] = useState('idle'); // idle, running, paused, stopped
  const [currentCampaignId, setCurrentCampaignId] = useState(null);
  const [sendingProgress, setSendingProgress] = useState({
    sent: 0,
    pending: 0,
    failed: 0,
    delivered: 0,
    total: 0
  });
  const [showPreview, setShowPreview] = useState(true);
  const [templates, setTemplates] = useState([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState('');
  const [availableTags, setAvailableTags] = useState([]);
  const [useRichEditor, setUseRichEditor] = useState(true);
  const fileInputRef = useRef(null);
  const progressIntervalRef = useRef(null);
  const { addToast } = useToast();

  // Fetch templates on mount
  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await fetch('http://const API_URL = import.meta.env.VITE_API_URL/api/v1/templates/');
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates || []);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const handleTemplateSelect = (templateId) => {
    setSelectedTemplateId(templateId);
    if (templateId) {
      const template = templates.find(t => t.id === parseInt(templateId));
      if (template) {
        setSubjectLine(template.subject);
        setEmailBody(template.body);
        setTimeout(() => {
          addToast('Template loaded successfully!', 'success');
        }, 0);
      }
    }
  };

  // Cleanup interval on unmount
  useEffect(() => {
    return () => {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    };
  }, []);

  // Dummy CSV data for preview
  const dummyData = {
    first_name: 'Rahul',
    last_name: 'Ojha',
    email: 'rahul.ojha@example.com',
    phone: '1234567890',
    company: 'Tech Corp'
  };

  // Personalization tags
  const tags = [
    { label: '{{first_name}}', value: '{first_name}' },
    { label: '{{last_name}}', value: '{last_name}' },
    { label: '{{email}}', value: '{email}' },
    { label: '{{phone}}', value: '{phone}' },
    { label: '{{company}}', value: '{company}' }
  ];

  // Handle file upload with backend
  const handleFileSelect = async (selectedFile) => {
    if (!selectedFile) return;
    
    setFile(selectedFile);
    setUploadProgress(0);
    
    // Simulate upload progress UI
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 10;
      });
    }, 200);

    // Read CSV file to get contact count AND extract columns
    try {
      const text = await selectedFile.text();
      const lines = text.split('\n').filter(line => line.trim());
      
      if (lines.length > 0) {
        // Extract column headers from first line
        const headers = lines[0].split(',').map(h => h.trim());
        setAvailableTags(headers);
        
        const contactCount = Math.max(0, lines.length - 1); // Minus header row
        
        setSendingProgress(prev => ({ 
          ...prev, 
          total: contactCount, 
          pending: contactCount 
        }));
        
        setTimeout(() => {
          addToast(`CSV uploaded! ${contactCount} contacts found with ${headers.length} columns`, 'success');
        }, 0);
      }
    } catch (error) {
      console.error('Error reading CSV:', error);
      setTimeout(() => {
        addToast('Error reading CSV file', 'error');
      }, 0);
    }
  };

  // Drag and drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.name.endsWith('.csv') || droppedFile.name.endsWith('.xlsx'))) {
      handleFileSelect(droppedFile);
    } else {
      setTimeout(() => {
        addToast('Please upload a CSV or Excel file', 'error');
      }, 0);
    }
  };

  // Replace personalization tags with dummy data for preview
  const renderPreview = (text) => {
    if (!text) return 'Your email content will appear here...';
    return text
      .replace(/{first_name}/g, dummyData.first_name)
      .replace(/{last_name}/g, dummyData.last_name)
      .replace(/{email}/g, dummyData.email)
      .replace(/{phone}/g, dummyData.phone)
      .replace(/{company}/g, dummyData.company);
  };

  // Fetch campaign progress from backend
  const fetchCampaignProgress = async (campaignId) => {
    try {
      const response = await fetch(`http://const API_URL = import.meta.env.VITE_API_URL/api/v1/campaigns/${campaignId}/progress`);
      if (response.ok) {
        const data = await response.json();
        
        setSendingProgress({
          sent: data.sent_count || data.sent || 0,
          pending: data.pending_count || data.pending || 0,
          failed: data.failed_count || data.failed || 0,
          delivered: data.delivered_count || data.delivered || 0,
          total: data.total_emails || data.total || 0
        });

        // Check if campaign is completed
        if (data.status === 'completed') {
          setCampaignStatus('stopped');
          if (progressIntervalRef.current) {
            clearInterval(progressIntervalRef.current);
          }
          setTimeout(() => {
            addToast('Campaign completed successfully!', 'success');
          }, 0);
        }
      }
    } catch (error) {
      console.error('Error fetching progress:', error);
    }
  };

  // Campaign controls with backend API
  const startCampaign = async () => {
    // Validation
    if (uploadMode === 'csv' && !file) {
      setTimeout(() => {
        addToast('Please upload a recipient list first', 'warning');
      }, 0);
      return;
    }
    
    if (uploadMode === 'manual' && !manualEmails.trim()) {
      setTimeout(() => {
        addToast('Please enter at least one email address', 'warning');
      }, 0);
      return;
    }
    
    if (!campaignName || !subjectLine || !emailBody) {
      setTimeout(() => {
        addToast('Please fill in all required fields', 'warning');
      }, 0);
      return;
    }

    try {
      // Step 1: Create campaign
      const campaignData = {
        campaign_name: campaignName,
        subject: subjectLine,
        template: emailBody
      };

      const createResponse = await fetch('http://const API_URL = import.meta.env.VITE_API_URL/api/v1/campaigns/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(campaignData)
      });

      if (!createResponse.ok) {
        throw new Error('Failed to create campaign');
      }

      const campaign = await createResponse.json();
      setCurrentCampaignId(campaign.id);

      // Step 2: Upload recipients
      let uploadResult;
      
      if (uploadMode === 'csv') {
        // CSV upload
        const formData = new FormData();
        formData.append('file', file);

        const uploadResponse = await fetch(
          `http://const API_URL = import.meta.env.VITE_API_URL/api/v1/campaigns/${campaign.id}/upload-recipients`,
          {
            method: 'POST',
            body: formData
          }
        );

        if (!uploadResponse.ok) {
          throw new Error('Failed to upload recipients');
        }

        uploadResult = await uploadResponse.json();
      } else {
        // Manual emails - create CSV and upload
        const emails = manualEmails.split(/[,\n]/).map(e => e.trim()).filter(e => e);
        
        // Create CSV content
        let csvContent = 'first_name,last_name,email,phone,company\n';
        emails.forEach((email, idx) => {
          const name = email.split('@')[0];
          csvContent += `User${idx + 1},Test,${email},1234567890,TestCompany\n`;
        });
        
        // Create CSV file
        const csvBlob = new Blob([csvContent], { type: 'text/csv' });
        const csvFile = new File([csvBlob], 'manual_contacts.csv', { type: 'text/csv' });
        
        const formData = new FormData();
        formData.append('file', csvFile);

        const uploadResponse = await fetch(
          `http://const API_URL = import.meta.env.VITE_API_URL/api/v1/campaigns/${campaign.id}/upload-recipients`,
          {
            method: 'POST',
            body: formData
          }
        );

        if (!uploadResponse.ok) {
          throw new Error('Failed to upload recipients');
        }

        uploadResult = await uploadResponse.json();
      }
      
      setSendingProgress(prev => ({
        ...prev,
        total: uploadResult.total_uploaded,
        pending: uploadResult.total_uploaded
      }));

      // Step 3: Start campaign
      const startResponse = await fetch(
        `http://const API_URL = import.meta.env.VITE_API_URL/api/v1/campaigns/${campaign.id}/start`,
        { method: 'POST' }
      );

      if (!startResponse.ok) {
        throw new Error('Failed to start campaign');
      }

      setCampaignStatus('running');
      setTimeout(() => {
        addToast('Campaign started successfully!', 'success');
      }, 0);

      // Start polling for progress
      progressIntervalRef.current = setInterval(() => {
        fetchCampaignProgress(campaign.id);
      }, 3000); // Poll every 3 seconds

    } catch (error) {
      console.error('Error starting campaign:', error);
      setTimeout(() => {
        addToast(`Error: ${error.message}`, 'error');
      }, 0);
    }
  };

  const pauseCampaign = async () => {
    if (!currentCampaignId) return;

    try {
      const response = await fetch(
        `http://const API_URL = import.meta.env.VITE_API_URL/api/v1/campaigns/${currentCampaignId}/pause`,
        { method: 'POST' }
      );

      if (response.ok) {
        setCampaignStatus('paused');
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current);
        }
        setTimeout(() => {
          addToast('Campaign paused', 'warning');
        }, 0);
      }
    } catch (error) {
      console.error('Error pausing campaign:', error);
    }
  };

  const stopCampaign = async () => {
    if (!currentCampaignId) return;

    try {
      const response = await fetch(
        `http://const API_URL = import.meta.env.VITE_API_URL/api/v1/campaigns/${currentCampaignId}/stop`,
        { method: 'POST' }
      );

      if (response.ok) {
        setCampaignStatus('stopped');
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current);
        }
        setTimeout(() => {
          addToast('Campaign stopped', 'error');
        }, 0);
      }
    } catch (error) {
      console.error('Error stopping campaign:', error);
    }
  };

  const insertTag = (tag) => {
    setEmailBody(prev => prev + tag);
  };

  const progressPercentage = sendingProgress.total > 0 
    ? ((sendingProgress.sent / sendingProgress.total) * 100).toFixed(1)
    : 0;

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
            <Zap className="w-9 h-9 text-white" />
          </div>
          <div>
            <h2 className="text-4xl font-black text-gray-900">Campaign Builder</h2>
            <p className="text-lg font-bold text-gray-700">Create and launch your email campaign</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className={`px-4 py-2 rounded-lg glass ${
            campaignStatus === 'running' ? 'border-green-500/50' :
            campaignStatus === 'paused' ? 'border-yellow-500/50' :
            'border-gray-500/50'
          } border`}>
            <span className="text-sm text-gray-400">Status: </span>
            <span className={`text-sm font-semibold ${
              campaignStatus === 'running' ? 'text-green-500' :
              campaignStatus === 'paused' ? 'text-yellow-500' :
              'text-gray-400'
            }`}>
              {campaignStatus.charAt(0).toUpperCase() + campaignStatus.slice(1)}
            </span>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Side: Form */}
        <div className="space-y-6">
          {/* Campaign Details */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card>
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 rounded-xl bg-blue-100 shadow-md">
                  <Mail className="w-7 h-7 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-2xl font-black text-gray-900">Campaign Details</h3>
                  <p className="text-base font-bold text-gray-700">Basic information about your campaign</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <Input
                  label="Campaign Name"
                  placeholder="e.g., Welcome Series - January"
                  value={campaignName}
                  onChange={(e) => setCampaignName(e.target.value)}
                  required
                />

                {/* Template Selector */}
                <div>
                  <label className="block text-base font-bold text-gray-700 mb-2">
                    Use Template (Optional)
                  </label>
                  <select
                    value={selectedTemplateId}
                    onChange={(e) => handleTemplateSelect(e.target.value)}
                    className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-300 rounded-xl text-gray-900 font-bold focus:outline-none focus:border-gold transition-colors shadow-sm"
                  >
                    <option value="">Create from scratch</option>
                    {templates.map(template => (
                      <option key={template.id} value={template.id}>
                        {template.name} - {template.category || 'General'}
                      </option>
                    ))}
                  </select>
                  <p className="text-sm font-semibold text-gray-600 mt-1">
                    Select a template to auto-fill subject and body
                  </p>
                </div>
                
                <Input
                  label="Subject Line"
                  placeholder="Use {first_name} for personalization"
                  value={subjectLine}
                  onChange={(e) => setSubjectLine(e.target.value)}
                  required
                />
              </div>
            </Card>
          </motion.div>

          {/* Upload Recipients */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card>
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-purple-100 shadow-md">
                    <User className="w-7 h-7 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-black text-gray-900">Upload Recipients</h3>
                    <p className="text-base font-bold text-gray-700">Add contacts via CSV or manually</p>
                  </div>
                </div>
              </div>

              {/* Upload Mode Tabs */}
              <div className="flex gap-2 mb-4">
                <button
                  onClick={() => setUploadMode('csv')}
                  className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all ${
                    uploadMode === 'csv'
                      ? 'bg-gold text-dark'
                      : 'bg-dark-light text-gray-400 hover:bg-dark-lighter'
                  }`}
                >
                  <UploadIcon className="w-4 h-4 inline mr-2" />
                  CSV Upload
                </button>
                <button
                  onClick={() => setUploadMode('manual')}
                  className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all ${
                    uploadMode === 'manual'
                      ? 'bg-gold text-dark'
                      : 'bg-dark-light text-gray-400 hover:bg-dark-lighter'
                  }`}
                >
                  <Mail className="w-4 h-4 inline mr-2" />
                  Manual Entry
                </button>
              </div>

              {/* CSV Upload Mode */}
              {uploadMode === 'csv' && (
                <>
                  <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer ${
                      isDragging 
                        ? 'border-gold bg-gold/5' 
                        : 'border-gray-700 hover:border-gold/50 hover:bg-gold/5'
                    }`}
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".csv,.xlsx"
                      onChange={(e) => handleFileSelect(e.target.files[0])}
                      className="hidden"
                    />
                    
                    {file ? (
                      <div className="space-y-4">
                        <div className="flex items-center justify-center gap-3">
                          <FileText className="w-8 h-8 text-gold" />
                          <div className="text-left">
                            <p className="text-gray-900 font-black">{file.name}</p>
                            <p className="text-sm font-bold text-gray-700">
                              {sendingProgress.total} contacts
                            </p>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setFile(null);
                              setSendingProgress({ sent: 0, pending: 0, failed: 0, delivered: 0, total: 0 });
                            }}
                            className="p-2 hover:bg-red-500/10 rounded-lg transition-colors"
                          >
                            <X className="w-5 h-5 text-red-400" />
                          </button>
                        </div>
                        
                        {uploadProgress < 100 && (
                          <div className="w-full bg-dark-light rounded-full h-2">
                            <motion.div
                              className="h-full bg-gradient-to-r from-gold to-gold-light rounded-full"
                              initial={{ width: 0 }}
                              animate={{ width: `${uploadProgress}%` }}
                            />
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="space-y-3">
                        <UploadIcon className="w-12 h-12 text-gray-600 mx-auto" />
                        <div>
                          <p className="text-gray-900 font-black">
                            Drag & drop your file here
                          </p>
                          <p className="text-sm font-bold text-gray-700 mt-1">
                            or click to browse (CSV, XLSX)
                          </p>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="p-4 rounded-xl bg-blue-50 border-2 border-blue-200">
                    <p className="text-sm font-bold text-blue-700">
                      📋 CSV Format: Any column headers will become available as tags!
                      <br />
                      Example: first_name, last_name, email, company, phone, city, etc.
                    </p>
                  </div>

                  {availableTags.length > 0 && (
                    <div className="p-4 rounded-xl bg-green-50 border-2 border-green-200">
                      <p className="text-sm font-bold text-green-700 mb-2">
                        ✓ {availableTags.length} columns detected:
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {availableTags.map(tag => (
                          <span key={tag} className="px-2 py-1 bg-green-100 text-green-700 rounded-lg text-xs font-bold">
                            {`{${tag}}`}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* Manual Entry Mode */}
              {uploadMode === 'manual' && (
                <>
                  <Textarea
                    label="Enter Email Addresses"
                    placeholder="Enter emails separated by commas or new lines:&#10;&#10;john@example.com, jane@example.com&#10;mike@example.com"
                    value={manualEmails}
                    onChange={(e) => {
                      setManualEmails(e.target.value);
                      // Count emails
                      const emails = e.target.value.split(/[,\n]/).map(e => e.trim()).filter(e => e);
                      setSendingProgress(prev => ({ ...prev, total: emails.length, pending: emails.length }));
                    }}
                    rows={8}
                  />
                  
                  {manualEmails && (
                    <div className="mt-3 p-3 rounded-lg bg-green-500/5 border border-green-500/20">
                      <p className="text-sm text-green-400">
                        ✓ {manualEmails.split(/[,\n]/).filter(e => e.trim()).length} email(s) detected
                      </p>
                    </div>
                  )}

                  <div className="mt-4 p-3 rounded-lg bg-gold/5 border border-gold/20">
                    <p className="text-sm text-gold">
                      💡 Tip: Paste multiple emails separated by commas or new lines. Perfect for quick testing!
                    </p>
                  </div>
                </>
              )}
            </Card>
          </motion.div>

          {/* Email Content */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card>
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 rounded-xl bg-green-100 shadow-md">
                  <Code className="w-7 h-7 text-green-600" />
                </div>
                <div>
                  <h3 className="text-2xl font-black text-gray-900">Email Content</h3>
                  <p className="text-base font-bold text-gray-700">Write your email message</p>
                </div>
              </div>

              {/* Email Content */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-3">
                  <label className="block text-base font-bold text-gray-700">
                    Email Body
                  </label>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => setUseRichEditor(true)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
                        useRichEditor 
                          ? 'bg-gold text-white' 
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      Rich Editor
                    </button>
                    <button
                      type="button"
                      onClick={() => setUseRichEditor(false)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
                        !useRichEditor 
                          ? 'bg-gold text-white' 
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      Plain Text
                    </button>
                  </div>
                </div>

                {!useRichEditor && (
                  /* Personalization Tags for Plain Text */
                  <div className="mb-3 p-4 bg-gradient-to-r from-gold/10 to-gold-light/10 border-2 border-gold/30 rounded-xl">
                    <label className="block text-base font-black text-gray-900 mb-3">
                      📋 Available Tags - Click to Insert
                      {availableTags.length > 0 && (
                        <span className="ml-2 px-2 py-1 bg-green-100 text-green-700 rounded-lg text-xs font-bold">
                          {availableTags.length} from CSV
                        </span>
                      )}
                    </label>
                    
                    {availableTags.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {availableTags.map(tag => (
                          <button
                            key={tag}
                            type="button"
                            onClick={() => {
                              setEmailBody(prev => prev + `{${tag}}`);
                              setTimeout(() => {
                                addToast(`Tag {${tag}} inserted!`, 'success');
                              }, 0);
                            }}
                            className="group px-4 py-2.5 rounded-xl bg-white border-2 border-gold/40 hover:border-gold hover:bg-gold/10 transition-all shadow-sm hover:shadow-md"
                          >
                            <span className="text-gold font-black text-sm group-hover:scale-110 inline-block transition-transform">
                              {`{${tag}}`}
                            </span>
                          </button>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-6 bg-white rounded-xl border-2 border-dashed border-gray-300">
                        <FileText className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                        <p className="text-sm font-bold text-gray-700">
                          Upload a CSV file to see available tags
                        </p>
                        <p className="text-xs font-semibold text-gray-600 mt-1">
                          All column headers will become clickable tags
                        </p>
                      </div>
                    )}
                    
                    <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <p className="text-xs font-bold text-blue-700">
                        💡 Tip: Tags will be replaced with actual data from your CSV when sending emails
                      </p>
                    </div>
                  </div>
                )}

                {useRichEditor ? (
                  <RichTextEditor
                    value={emailBody}
                    onChange={setEmailBody}
                    placeholder="Dear {first_name},&#10;&#10;Welcome to our platform!&#10;&#10;Best regards,&#10;Team"
                    availableTags={availableTags}
                  />
                ) : (
                  <Textarea
                    placeholder="Dear {first_name},&#10;&#10;Welcome to our platform!&#10;&#10;Best regards,&#10;Team"
                    value={emailBody}
                    onChange={(e) => setEmailBody(e.target.value)}
                    rows={14}
                    required
                  />
                )}
              </div>
            </Card>
          </motion.div>

          {/* Campaign Controls */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card>
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 rounded-xl bg-gold/20 shadow-md">
                  <Activity className="w-7 h-7 text-gold" />
                </div>
                <div>
                  <h3 className="text-2xl font-black text-gray-900">Campaign Controls</h3>
                  <p className="text-base font-bold text-gray-700">Start, pause or stop your campaign</p>
                </div>
              </div>

              <div className="flex gap-3">
                <Button
                  onClick={startCampaign}
                  disabled={campaignStatus === 'running'}
                  variant="primary"
                  className="flex-1"
                >
                  <Play className="w-4 h-4 mr-2" />
                  Start Campaign
                </Button>
                
                <Button
                  onClick={pauseCampaign}
                  disabled={campaignStatus !== 'running'}
                  variant="secondary"
                  className="flex-1"
                >
                  <Pause className="w-4 h-4 mr-2" />
                  Pause
                </Button>
                
                <Button
                  onClick={stopCampaign}
                  disabled={campaignStatus === 'idle'}
                  variant="danger"
                  className="flex-1"
                >
                  <Square className="w-4 h-4 mr-2" />
                  Stop
                </Button>
              </div>
            </Card>
          </motion.div>
        </div>

        {/* Right Side: Preview & Progress */}
        <div className="space-y-6">
          {/* Live Preview */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card>
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-gold/10">
                    <Eye className="w-5 h-5 text-gold" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">Live Preview</h3>
                    <p className="text-sm text-gray-400">How your email will look</p>
                  </div>
                </div>
              </div>

              {/* Email Preview */}
              <div className="space-y-4">
                {/* Subject Preview */}
                <div className="p-5 rounded-xl bg-gray-100 border-2 border-gray-300 shadow-sm">
                  <p className="text-sm font-bold text-gray-700 mb-1">Subject:</p>
                  <p className="text-gray-900 font-black text-base">
                    {renderPreview(subjectLine) || 'Your subject line will appear here...'}
                  </p>
                </div>

                {/* Body Preview */}
                <div className="p-6 rounded-xl bg-gray-50 border-2 border-gray-300 min-h-[400px] shadow-inner">
                  <div className="prose prose-invert max-w-none">
                    <pre className="whitespace-pre-wrap font-sans text-gray-900 font-semibold text-sm leading-relaxed">
                      {renderPreview(emailBody)}
                    </pre>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-yellow-50 border-2 border-yellow-200">
                  <p className="text-sm font-bold text-yellow-800">
                    ℹ️ Preview uses sample data. Actual emails will use real recipient data.
                  </p>
                </div>
              </div>
            </Card>
          </motion.div>

          {/* Sending Progress */}
          <AnimatePresence>
            {campaignStatus !== 'idle' && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <Card>
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-3 rounded-xl bg-gold/20 shadow-md">
                    <Activity className="w-7 h-7 text-gold animate-pulse" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-black text-gray-900">Sending Progress</h3>
                    <p className="text-base font-bold text-gray-700">Real-time campaign statistics</p>
                  </div>
                </div>

                  {/* Progress Bar */}
                  <div className="mb-6">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-base font-bold text-gray-700">Overall Progress</span>
                      <span className="text-base font-black text-gray-900">{progressPercentage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden shadow-inner">
                      <motion.div
                        className="h-full bg-gradient-to-r from-gold to-gold-light rounded-full shadow-md"
                        initial={{ width: 0 }}
                        animate={{ width: `${progressPercentage}%` }}
                        transition={{ duration: 0.5 }}
                      />
                    </div>
                  </div>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-5 rounded-xl bg-blue-100 border-2 border-blue-300 shadow-md">
                      <div className="flex items-center gap-3 mb-2">
                        <Send className="w-6 h-6 text-blue-600" />
                        <p className="text-sm font-bold text-gray-700">Total Emails</p>
                      </div>
                      <p className="text-3xl font-black text-gray-900">{sendingProgress.total}</p>
                    </div>

                    <div className="p-5 rounded-xl bg-green-100 border-2 border-green-300 shadow-md">
                      <div className="flex items-center gap-3 mb-2">
                        <Check className="w-6 h-6 text-green-600" />
                        <p className="text-sm font-bold text-gray-700">Sent</p>
                      </div>
                      <p className="text-3xl font-black text-gray-900">{sendingProgress.sent}</p>
                    </div>

                    <div className="p-5 rounded-xl bg-purple-100 border-2 border-purple-300 shadow-md">
                      <div className="flex items-center gap-3 mb-2">
                        <CheckCircle className="w-6 h-6 text-purple-600" />
                        <p className="text-sm font-bold text-gray-700">Delivered</p>
                      </div>
                      <p className="text-3xl font-black text-gray-900">{sendingProgress.delivered}</p>
                    </div>

                    <div className="p-5 rounded-xl bg-red-100 border-2 border-red-300 shadow-md">
                      <div className="flex items-center gap-3 mb-2">
                        <XCircle className="w-6 h-6 text-red-600" />
                        <p className="text-sm font-bold text-gray-700">Failed</p>
                      </div>
                      <p className="text-3xl font-black text-gray-900">{sendingProgress.failed}</p>
                    </div>

                    <div className="p-5 rounded-xl bg-yellow-100 border-2 border-yellow-300 shadow-md col-span-2">
                      <div className="flex items-center gap-3 mb-2">
                        <Clock className="w-6 h-6 text-yellow-600" />
                        <p className="text-sm font-bold text-gray-700">Pending</p>
                      </div>
                      <p className="text-3xl font-black text-gray-900">{sendingProgress.pending}</p>
                    </div>
                  </div>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default CampaignBuilder;
