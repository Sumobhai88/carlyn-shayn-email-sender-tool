import { 
  Server, CheckCircle, Plus, Edit2, Trash2, 
  Zap, Mail, Building2, Eye, EyeOff, AlertCircle,
  Check, X, Loader2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import Modal from '../components/Modal';
import { useState, useEffect } from 'react';
import { useToast } from '../components/Toast';

const SMTPSettings = () => {
  const { addToast } = useToast();
  const [showAddModal, setShowAddModal] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [editingProfile, setEditingProfile] = useState(null);
  const [testingConnection, setTestingConnection] = useState(null);
  const [loading, setLoading] = useState(true);
  const [profiles, setProfiles] = useState([]);

  // Form state
  const [formData, setFormData] = useState({
    profile_name: '',
    sender_name: '',
    sender_email: '',
    smtp_host: '',
    smtp_port: '587',
    username: '',
    password: '',
    tls_enabled: true
  });

  // Fetch SMTP profiles from backend
  useEffect(() => {
    fetchProfiles();
  }, []);

  const fetchProfiles = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/smtp-profiles/');
      if (response.ok) {
        const data = await response.json();
        setProfiles(data);
      } else {
        setTimeout(() => {
          addToast('Failed to fetch SMTP profiles', 'error');
        }, 0);
      }
    } catch (error) {
      console.error('Error fetching profiles:', error);
      setTimeout(() => {
        addToast('Error connecting to backend', 'error');
      }, 0);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      profile_name: '',
      sender_name: '',
      sender_email: '',
      smtp_host: '',
      smtp_port: '587',
      username: '',
      password: '',
      tls_enabled: true
    });
    setEditingProfile(null);
    setShowPassword(false);
  };

  const handleSubmit = async () => {
    // Validate
    if (!formData.profile_name || !formData.sender_email || !formData.smtp_host) {
      setTimeout(() => {
        addToast('Please fill in all required fields', 'warning');
      }, 0);
      return;
    }

    try {
      if (editingProfile) {
        // Update existing profile
        const response = await fetch(
          `http://localhost:8000/api/v1/smtp-profiles/${editingProfile.id}`,
          {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
          }
        );

        if (response.ok) {
          setTimeout(() => {
            addToast('SMTP profile updated successfully!', 'success');
          }, 0);
          await fetchProfiles();
        } else {
          const error = await response.json();
          throw new Error(error.detail || 'Failed to update profile');
        }
      } else {
        // Add new profile
        const response = await fetch('http://localhost:8000/api/v1/smtp-profiles/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        });

        if (response.ok) {
          setTimeout(() => {
            addToast('SMTP profile added successfully!', 'success');
          }, 0);
          await fetchProfiles();
        } else {
          const error = await response.json();
          throw new Error(error.detail || 'Failed to add profile');
        }
      }

      setShowAddModal(false);
      resetForm();
    } catch (error) {
      console.error('Error saving profile:', error);
      setTimeout(() => {
        addToast(error.message, 'error');
      }, 0);
    }
  };

  const handleEdit = (profile) => {
    setEditingProfile(profile);
    setFormData({
      profile_name: profile.profile_name,
      sender_name: profile.sender_name,
      sender_email: profile.sender_email,
      smtp_host: profile.smtp_host,
      smtp_port: profile.smtp_port.toString(),
      username: profile.username,
      password: '', // Don't show existing password
      tls_enabled: profile.tls_enabled
    });
    setShowAddModal(true);
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this SMTP profile?')) {
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/smtp-profiles/${id}`,
        { method: 'DELETE' }
      );

      if (response.ok) {
        setTimeout(() => {
          addToast('SMTP profile deleted', 'success');
        }, 0);
        await fetchProfiles();
      } else {
        throw new Error('Failed to delete profile');
      }
    } catch (error) {
      console.error('Error deleting profile:', error);
      setTimeout(() => {
        addToast('Failed to delete profile', 'error');
      }, 0);
    }
  };

  const handleSetActive = async (id) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/smtp-profiles/${id}/set-active`,
        { method: 'POST' }
      );

      if (response.ok) {
        setTimeout(() => {
          addToast('Active SMTP profile updated', 'success');
        }, 0);
        await fetchProfiles();
      } else {
        throw new Error('Failed to activate profile');
      }
    } catch (error) {
      console.error('Error activating profile:', error);
      setTimeout(() => {
        addToast('Failed to activate profile', 'error');
      }, 0);
    }
  };

  const handleTestConnection = async (id) => {
    setTestingConnection(id);

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/smtp-profiles/${id}/test`,
        { method: 'POST' }
      );

      const result = await response.json();

      if (response.ok) {
        setTimeout(() => {
          addToast(result.message || 'Connection test successful!', 'success');
        }, 0);
        await fetchProfiles();
      } else {
        setTimeout(() => {
          addToast(result.detail || 'Connection test failed', 'error');
        }, 0);
      }
    } catch (error) {
      console.error('Error testing connection:', error);
      setTimeout(() => {
        addToast('Connection test failed', 'error');
      }, 0);
    } finally {
      setTestingConnection(null);
    }
  };

  const connectedCount = profiles.filter(p => p.status === 'connected').length;
  const failedCount = profiles.filter(p => p.status === 'failed').length;
  const activeProfile = profiles.find(p => p.is_active);

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
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-xl">
            <Server className="w-9 h-9 text-white" />
          </div>
          <div>
            <h2 className="text-4xl font-black text-gray-900">SMTP Settings</h2>
            <p className="text-lg font-bold text-gray-700">Manage your email sending servers</p>
          </div>
        </div>
        <Button icon={Plus} onClick={() => { resetForm(); setShowAddModal(true); }}>
          Add SMTP Profile
        </Button>
      </motion.div>

      {/* Connection Status Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card padding="lg">
          <h3 className="text-2xl font-black text-gray-900 mb-6">Connection Status</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gray-50 border-2 border-gray-300 rounded-xl p-5 shadow-sm hover:shadow-md transition-all">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center shadow-md">
                  <CheckCircle className="w-7 h-7 text-green-600" />
                </div>
                <div>
                  <p className="text-base font-bold text-gray-700">Connected</p>
                  <p className="text-3xl font-black text-gray-900">{connectedCount}</p>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 border-2 border-gray-300 rounded-xl p-5 shadow-sm hover:shadow-md transition-all">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-red-100 flex items-center justify-center shadow-md">
                  <AlertCircle className="w-7 h-7 text-red-600" />
                </div>
                <div>
                  <p className="text-base font-bold text-gray-700">Failed</p>
                  <p className="text-3xl font-black text-gray-900">{failedCount}</p>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 border-2 border-gray-300 rounded-xl p-5 shadow-sm hover:shadow-md transition-all">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-gold/20 flex items-center justify-center shadow-md">
                  <Check className="w-7 h-7 text-gold" />
                </div>
                <div>
                  <p className="text-base font-bold text-gray-700">Active Profile</p>
                  <p className="text-lg font-black text-gray-900 truncate">
                    {activeProfile?.profile_name || 'None'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* SMTP Profiles List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="space-y-4"
      >
        <h3 className="text-2xl font-black text-gray-900">Your SMTP Profiles</h3>
        
        {profiles.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <Server className="w-20 h-20 text-gray-400 mx-auto mb-4" />
              <h3 className="text-2xl font-black text-gray-900 mb-2">No SMTP Profiles</h3>
              <p className="text-lg font-bold text-gray-700 mb-6">Add your first SMTP profile to start sending emails</p>
              <Button icon={Plus} onClick={() => setShowAddModal(true)}>
                Add SMTP Profile
              </Button>
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            <AnimatePresence>
              {profiles.map((profile, index) => (
                <motion.div
                  key={profile.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -100 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Card hover className={`${profile.is_active ? 'border-gold border-2' : ''}`}>
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4 flex-1">
                        <div className={`w-14 h-14 rounded-xl shadow-md ${
                          profile.status === 'connected' ? 'bg-green-100' :
                          profile.status === 'failed' ? 'bg-red-100' :
                          'bg-gray-100'
                        } flex items-center justify-center flex-shrink-0`}>
                          <Mail className={`w-8 h-8 ${
                            profile.status === 'connected' ? 'text-green-600' :
                            profile.status === 'failed' ? 'text-red-600' :
                            'text-gray-500'
                          }`} />
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-2">
                            <h4 className="text-xl font-black text-gray-900">
                              {profile.profile_name}
                            </h4>
                            {profile.is_active && (
                              <span className="px-3 py-1 bg-gold/20 text-gold text-xs font-black rounded-full">
                                Active
                              </span>
                            )}
                            <span className={`px-3 py-1 text-xs font-black rounded-full ${
                              profile.status === 'connected' ? 'bg-green-100 text-green-700' :
                              profile.status === 'failed' ? 'bg-red-100 text-red-700' :
                              'bg-gray-100 text-gray-700'
                            }`}>
                              {profile.status === 'connected' ? 'Connected' :
                               profile.status === 'failed' ? 'Failed' :
                               'Testing'}
                            </span>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                            <div>
                              <span className="text-gray-700 font-bold">Sender: </span>
                              <span className="text-gray-900 font-black">{profile.sender_name}</span>
                            </div>
                            <div>
                              <span className="text-gray-700 font-bold">Email: </span>
                              <span className="text-gray-900 font-black">{profile.sender_email}</span>
                            </div>
                            <div>
                              <span className="text-gray-700 font-bold">Host: </span>
                              <span className="text-gray-900 font-black">{profile.smtp_host}</span>
                            </div>
                            <div>
                              <span className="text-gray-700 font-bold">Port: </span>
                              <span className="text-gray-900 font-black">
                                {profile.smtp_port} {profile.tls_enabled && '(TLS)'}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 flex-shrink-0 ml-4">
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => handleEdit(profile)}
                        >
                          <Edit2 className="w-5 h-5" />
                        </Button>
                        
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => handleTestConnection(profile.id)}
                          disabled={testingConnection === profile.id}
                        >
                          {testingConnection === profile.id ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                          ) : (
                            'Test'
                          )}
                        </Button>
                        
                        {!profile.is_active && (
                          <Button
                            size="sm"
                            variant="primary"
                            onClick={() => handleSetActive(profile.id)}
                          >
                            Set Active
                          </Button>
                        )}
                        
                        <Button
                          size="sm"
                          variant="danger"
                          onClick={() => handleDelete(profile.id)}
                        >
                          <Trash2 className="w-5 h-5" />
                        </Button>
                      </div>
                    </div>
                  </Card>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </motion.div>

      {/* Add/Edit Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => {
          setShowAddModal(false);
          resetForm();
        }}
        title={editingProfile ? 'Edit SMTP Profile' : 'Add SMTP Profile'}
      >
        <div className="space-y-4">
          <Input
            label="Profile Name"
            placeholder="e.g., Gmail SMTP"
            value={formData.profile_name}
            onChange={(e) => setFormData({ ...formData, profile_name: e.target.value })}
            required
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Sender Name"
              placeholder="Your Name"
              value={formData.sender_name}
              onChange={(e) => setFormData({ ...formData, sender_name: e.target.value })}
              required
            />
            <Input
              label="Sender Email"
              type="email"
              placeholder="you@example.com"
              value={formData.sender_email}
              onChange={(e) => setFormData({ ...formData, sender_email: e.target.value })}
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="SMTP Host"
              placeholder="smtp.gmail.com"
              value={formData.smtp_host}
              onChange={(e) => setFormData({ ...formData, smtp_host: e.target.value })}
              required
            />
            <Input
              label="SMTP Port"
              type="number"
              placeholder="587"
              value={formData.smtp_port}
              onChange={(e) => setFormData({ ...formData, smtp_port: e.target.value })}
              required
            />
          </div>

          <Input
            label="Username"
            placeholder="your-email@gmail.com"
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
            required
          />

          <div className="relative">
            <Input
              label="Password"
              type={showPassword ? 'text' : 'password'}
              placeholder={editingProfile ? 'Leave empty to keep current' : 'Your password or app password'}
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required={!editingProfile}
            />
            <button
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-[38px] p-2 hover:bg-white/5 rounded transition-colors"
            >
              {showPassword ? (
                <EyeOff className="w-5 h-5 text-gray-400" />
              ) : (
                <Eye className="w-5 h-5 text-gray-400" />
              )}
            </button>
          </div>

          <div className="flex items-center gap-3 p-5 rounded-xl bg-gray-50 border-2 border-gray-300 shadow-sm">
            <input
              type="checkbox"
              id="tls"
              checked={formData.tls_enabled}
              onChange={(e) => setFormData({ ...formData, tls_enabled: e.target.checked })}
              className="w-6 h-6 rounded border-gray-600 text-gold focus:ring-gold"
            />
            <label htmlFor="tls" className="text-gray-900 font-bold cursor-pointer">
              Enable TLS/SSL (Recommended)
            </label>
          </div>

          <div className="p-5 rounded-xl bg-blue-50 border-2 border-blue-200">
            <p className="text-sm font-bold text-blue-700">
              💡 For Gmail, use App Password instead of your regular password.
              <br />
              Enable 2FA, then generate an App Password from your Google Account settings.
            </p>
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              variant="secondary"
              onClick={() => {
                setShowAddModal(false);
                resetForm();
              }}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleSubmit}
              className="flex-1"
            >
              {editingProfile ? 'Update Profile' : 'Add Profile'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default SMTPSettings;
