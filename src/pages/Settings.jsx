import { useState, useEffect } from 'react';
import { Settings as SettingsIcon, User, Bell, Loader2, Save, Mail, Shield } from 'lucide-react';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import { useToast } from '../components/Toast';
import { api } from '../utils/api';

const Settings = ({ user: propUser }) => {
  const { addToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [profile, setProfile] = useState({
    name: '',
    email: '',
    company_name: '',
  });

  const [notifPrefs, setNotifPrefs] = useState({
    notif_email: true,
    notif_campaigns: true,
  });

  const [usage, setUsage] = useState({ email_limit: 1000, emails_used: 0, remaining: 1000, percentage_used: 0, is_blocked: false });
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    fetchSettings();
    fetchUsage();
  }, []);

  const fetchUsage = async () => {
    try {
      const res = await api.get('/api/v1/settings/usage');
      if (res.ok) {
        setUsage(await res.json());
      }
    } catch (e) {}
  };

  const fetchSettings = async () => {
    try {
      const res = await api.get('/api/v1/settings/profile');
      if (res.ok) {
        const data = await res.json();
        setProfile({
          name: data.name || '',
          email: data.email || '',
          company_name: data.company_name || '',
        });
        setNotifPrefs({
          notif_email: data.notif_email ?? true,
          notif_campaigns: data.notif_campaigns ?? true,
        });
        setIsAdmin(data.is_superuser || false);
      }
    } catch (e) {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    setSaving(true);
    try {
      const res = await api.put('/api/v1/settings/profile', {
        name: profile.name,
        company_name: profile.company_name,
      });
      if (res.ok) {
        addToast('Profile updated successfully!', 'success');
      } else {
        addToast('Failed to update profile', 'error');
      }
    } catch (e) {
      addToast('Failed to update profile', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleNotifToggle = async (key) => {
    const newVal = !notifPrefs[key];
    const newPrefs = { ...notifPrefs, [key]: newVal };
    setNotifPrefs(newPrefs);

    try {
      const res = await api.put('/api/v1/settings/notifications/preferences', {
        [key]: newVal,
      });
      if (res.ok) {
        addToast('Notification preference saved', 'success');
      }
    } catch (e) {
      // revert
      setNotifPrefs(notifPrefs);
      addToast('Failed to save preference', 'error');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-gold animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-3xl">
      {/* Email Usage / Limit */}
      <Card padding="lg">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-xl">
            <Mail className="w-9 h-9 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-black text-gray-900">Email Usage</h2>
            <p className="text-base font-bold text-gray-700">Your sending limit and usage</p>
          </div>
        </div>

        {usage.is_blocked && (
          <div className="mb-4 p-4 bg-red-50 border-2 border-red-300 rounded-xl">
            <p className="text-sm font-black text-red-700">
              ⛔ Your email service has been blocked by the administrator. Contact support.
            </p>
          </div>
        )}

        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="p-4 bg-gray-50 rounded-xl border-2 border-gray-200 text-center">
            <p className="text-3xl font-black text-gray-900">{usage.emails_used}</p>
            <p className="text-xs font-bold text-gray-600 mt-1">Used</p>
          </div>
          <div className="p-4 bg-green-50 rounded-xl border-2 border-green-200 text-center">
            <p className="text-3xl font-black text-green-600">{usage.remaining}</p>
            <p className="text-xs font-bold text-gray-600 mt-1">Remaining</p>
          </div>
          <div className="p-4 bg-blue-50 rounded-xl border-2 border-blue-200 text-center">
            <p className="text-3xl font-black text-blue-600">{usage.email_limit}</p>
            <p className="text-xs font-bold text-gray-600 mt-1">Total Limit</p>
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm font-bold mb-2">
            <span className="text-gray-700">Usage</span>
            <span className={usage.percentage_used >= 90 ? 'text-red-600' : 'text-gray-700'}>
              {usage.percentage_used}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className={`h-3 rounded-full transition-all ${
                usage.percentage_used >= 90 ? 'bg-red-500' :
                usage.percentage_used >= 70 ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${Math.min(100, usage.percentage_used)}%` }}
            />
          </div>
          {usage.percentage_used >= 90 && (
            <p className="text-xs font-bold text-red-600 mt-2">
              ⚠️ You're running low on emails. Contact admin to increase your limit.
            </p>
          )}
        </div>

        {isAdmin && (
          <div className="mt-6 pt-6 border-t-2 border-gray-200">
            <Button onClick={() => { window.location.href = '/admin'; }}>
              <Shield className="w-4 h-4 mr-2 inline" />
              Open Admin Panel
            </Button>
          </div>
        )}
      </Card>

      {/* Profile Settings */}
      <Card padding="lg">
        <div className="flex items-center gap-4 mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center shadow-xl">
            <User className="w-9 h-9 text-white" />
          </div>
          <div>
            <h2 className="text-3xl font-black text-gray-900">Profile Settings</h2>
            <p className="text-lg font-bold text-gray-700">Manage your account information</p>
          </div>
        </div>

        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Input
              label="Full Name"
              value={profile.name}
              onChange={(e) => setProfile({ ...profile, name: e.target.value })}
              placeholder="Your name"
            />
            <div>
              <label className="block text-base font-bold text-gray-700 mb-2">Email Address</label>
              <input
                value={profile.email}
                disabled
                className="w-full px-4 py-3 bg-gray-100 border-2 border-gray-200 rounded-xl text-gray-500 font-semibold cursor-not-allowed"
              />
              <p className="text-xs text-gray-500 mt-1 font-semibold">Email cannot be changed (linked to Google)</p>
            </div>
          </div>

          <Input
            label="Company Name"
            value={profile.company_name}
            onChange={(e) => setProfile({ ...profile, company_name: e.target.value })}
            placeholder="Your company"
          />

          <div className="flex gap-4 pt-2">
            <Button onClick={handleSaveProfile} disabled={saving}>
              {saving ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin inline" />Saving...</>
              ) : (
                <><Save className="w-4 h-4 mr-2 inline" />Save Changes</>
              )}
            </Button>
            <Button variant="secondary" onClick={fetchSettings}>Cancel</Button>
          </div>
        </div>
      </Card>

      {/* Notifications */}
      <Card padding="lg">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-yellow-500 to-yellow-600 flex items-center justify-center shadow-xl">
            <Bell className="w-9 h-9 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-black text-gray-900">Notifications</h2>
            <p className="text-base font-bold text-gray-700">Configure how you receive updates</p>
          </div>
        </div>

        <div className="space-y-4">
          {[
            { key: 'notif_email', label: 'Email notifications', desc: 'Receive updates via email' },
            { key: 'notif_campaigns', label: 'Campaign alerts', desc: 'Get notified when campaigns start or complete' },
          ].map(({ key, label, desc }) => (
            <label
              key={key}
              className="flex items-center justify-between p-5 bg-gray-50 border-2 border-gray-300 hover:border-gold hover:shadow-lg rounded-xl cursor-pointer transition-all"
              onClick={() => handleNotifToggle(key)}
            >
              <div>
                <span className="text-gray-900 font-bold text-base block">{label}</span>
                <span className="text-gray-600 text-sm font-semibold">{desc}</span>
              </div>
              <div className={`relative w-12 h-6 rounded-full transition-colors ${notifPrefs[key] ? 'bg-gold' : 'bg-gray-300'}`}>
                <div className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${notifPrefs[key] ? 'translate-x-7' : 'translate-x-1'}`} />
              </div>
            </label>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default Settings;
