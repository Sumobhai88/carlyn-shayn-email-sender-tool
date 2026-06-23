import { Settings as SettingsIcon, User, Bell, Shield } from 'lucide-react';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import { useToast } from '../components/Toast';

const Settings = () => {
  const { addToast } = useToast();

  return (
    <div className="space-y-8">
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
            <Input label="Full Name" placeholder="Admin User" />
            <Input label="Email Address" placeholder="admin@carlyshayn.com" />
          </div>

          <Input label="Company Name" placeholder="Carlyn Shayn Inc." />

          <div className="flex gap-4 pt-6">
            <Button onClick={() => addToast('Settings updated!', 'success')}>
              Save Changes
            </Button>
            <Button variant="secondary">Cancel</Button>
          </div>
        </div>
      </Card>

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
          <label className="flex items-center justify-between p-5 bg-gray-50 border-2 border-gray-300 hover:border-gold hover:shadow-lg rounded-xl cursor-pointer transition-all">
            <span className="text-gray-900 font-bold text-base">Email notifications</span>
            <input type="checkbox" className="w-6 h-6 accent-gold" defaultChecked />
          </label>
          <label className="flex items-center justify-between p-5 bg-gray-50 border-2 border-gray-300 hover:border-gold hover:shadow-lg rounded-xl cursor-pointer transition-all">
            <span className="text-gray-900 font-bold text-base">Campaign alerts</span>
            <input type="checkbox" className="w-6 h-6 accent-gold" defaultChecked />
          </label>
        </div>
      </Card>
    </div>
  );
};

export default Settings;
