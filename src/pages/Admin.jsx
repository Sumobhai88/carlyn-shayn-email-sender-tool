import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Shield, Users, Ban, CheckCircle, Mail, Loader2,
  TrendingUp, Edit2, RotateCcw, Crown, ArrowLeft, X
} from 'lucide-react';
import Card from '../components/Card';
import Button from '../components/Button';
import { useToast } from '../components/Toast';
import { api } from '../utils/api';

const Admin = () => {
  const { addToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState({ total_users: 0, blocked_users: 0, admin_users: 0 });
  const [editingUser, setEditingUser] = useState(null);
  const [newLimit, setNewLimit] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const res = await api.get('/api/v1/admin/users');
      if (res.ok) {
        const data = await res.json();
        setUsers(data.users || []);
        setStats({
          total_users: data.total_users || 0,
          blocked_users: data.blocked_users || 0,
          admin_users: data.admin_users || 0,
        });
      } else if (res.status === 403) {
        addToast('Admin access required', 'error');
      }
    } catch (e) {
      addToast('Failed to load users', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSetLimit = async (userId) => {
    const limit = parseInt(newLimit);
    if (isNaN(limit) || limit < 0) {
      addToast('Enter a valid limit', 'error');
      return;
    }
    try {
      const res = await api.put(`/api/v1/admin/users/${userId}/limit`, { email_limit: limit });
      if (res.ok) {
        addToast(`Limit updated to ${limit}`, 'success');
        setEditingUser(null);
        setNewLimit('');
        fetchUsers();
      }
    } catch (e) {
      addToast('Failed to update limit', 'error');
    }
  };

  const handleBlock = async (userId, currentlyBlocked) => {
    try {
      const res = await api.post(`/api/v1/admin/users/${userId}/block`, { is_blocked: !currentlyBlocked });
      if (res.ok) {
        addToast(currentlyBlocked ? 'User unblocked' : 'User blocked', currentlyBlocked ? 'success' : 'warning');
        fetchUsers();
      } else {
        const err = await res.json();
        addToast(err.detail || 'Action failed', 'error');
      }
    } catch (e) {
      addToast('Failed', 'error');
    }
  };

  const handleResetUsage = async (userId) => {
    try {
      const res = await api.post(`/api/v1/admin/users/${userId}/reset-usage`);
      if (res.ok) {
        addToast('Usage reset to 0', 'success');
        fetchUsers();
      }
    } catch (e) {
      addToast('Failed', 'error');
    }
  };

  const handleToggleAdmin = async (userId) => {
    try {
      const res = await api.post(`/api/v1/admin/users/${userId}/make-admin`);
      if (res.ok) {
        addToast('Admin status changed', 'success');
        fetchUsers();
      }
    } catch (e) {
      addToast('Failed', 'error');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="w-10 h-10 text-gold animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-red-500 to-red-600 flex items-center justify-center shadow-xl">
              <Shield className="w-9 h-9 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-black text-gray-900">Admin Panel</h1>
              <p className="text-lg font-bold text-gray-700">Manage users, limits & service access</p>
            </div>
          </div>
          <Button variant="secondary" onClick={() => { window.location.href = '/'; }}>
            <ArrowLeft className="w-4 h-4 mr-2 inline" />
            Back to App
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card>
            <div className="flex items-center gap-3">
              <div className="p-4 bg-blue-100 rounded-xl"><Users className="w-7 h-7 text-blue-600" /></div>
              <div>
                <p className="text-base font-bold text-gray-700">Total Users</p>
                <h3 className="text-3xl font-black text-gray-900">{stats.total_users}</h3>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-3">
              <div className="p-4 bg-red-100 rounded-xl"><Ban className="w-7 h-7 text-red-600" /></div>
              <div>
                <p className="text-base font-bold text-gray-700">Blocked</p>
                <h3 className="text-3xl font-black text-gray-900">{stats.blocked_users}</h3>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-3">
              <div className="p-4 bg-gold/20 rounded-xl"><Crown className="w-7 h-7 text-gold" /></div>
              <div>
                <p className="text-base font-bold text-gray-700">Admins</p>
                <h3 className="text-3xl font-black text-gray-900">{stats.admin_users}</h3>
              </div>
            </div>
          </Card>
        </div>

        {/* Users Table */}
        <Card>
          <h2 className="text-2xl font-black text-gray-900 mb-6">All Users</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-200 text-left">
                  <th className="pb-3 text-sm font-black text-gray-700">User</th>
                  <th className="pb-3 text-sm font-black text-gray-700">Usage</th>
                  <th className="pb-3 text-sm font-black text-gray-700">Limit</th>
                  <th className="pb-3 text-sm font-black text-gray-700">Campaigns</th>
                  <th className="pb-3 text-sm font-black text-gray-700">Status</th>
                  <th className="pb-3 text-sm font-black text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {users.map((u) => {
                  const pct = u.email_limit > 0 ? Math.min(100, (u.emails_used / u.email_limit) * 100) : 0;
                  return (
                    <tr key={u.id} className="hover:bg-gray-50">
                      {/* User */}
                      <td className="py-4">
                        <div className="flex items-center gap-3">
                          {u.picture ? (
                            <img src={u.picture} alt="" className="w-9 h-9 rounded-full" />
                          ) : (
                            <div className="w-9 h-9 rounded-full bg-gold/20 flex items-center justify-center">
                              <Mail className="w-4 h-4 text-gold" />
                            </div>
                          )}
                          <div>
                            <p className="font-black text-gray-900 text-sm flex items-center gap-1">
                              {u.name || 'No name'}
                              {u.is_superuser && <Crown className="w-3.5 h-3.5 text-gold" />}
                            </p>
                            <p className="text-xs font-semibold text-gray-600">{u.email}</p>
                          </div>
                        </div>
                      </td>

                      {/* Usage */}
                      <td className="py-4">
                        <div className="w-32">
                          <div className="flex justify-between text-xs font-bold mb-1">
                            <span className="text-gray-700">{u.emails_used}/{u.email_limit}</span>
                            <span className={pct >= 90 ? 'text-red-600' : 'text-gray-500'}>{pct.toFixed(0)}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${pct >= 90 ? 'bg-red-500' : pct >= 70 ? 'bg-yellow-500' : 'bg-green-500'}`}
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                        </div>
                      </td>

                      {/* Limit edit */}
                      <td className="py-4">
                        {editingUser === u.id ? (
                          <div className="flex items-center gap-1">
                            <input
                              type="number"
                              value={newLimit}
                              onChange={(e) => setNewLimit(e.target.value)}
                              className="w-20 px-2 py-1 border-2 border-gold rounded-lg text-sm font-bold"
                              placeholder={u.email_limit}
                              autoFocus
                            />
                            <button onClick={() => handleSetLimit(u.id)} className="p-1.5 bg-green-100 rounded-lg hover:bg-green-200">
                              <CheckCircle className="w-4 h-4 text-green-600" />
                            </button>
                            <button onClick={() => { setEditingUser(null); setNewLimit(''); }} className="p-1.5 bg-gray-100 rounded-lg hover:bg-gray-200">
                              <X className="w-4 h-4 text-gray-600" />
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => { setEditingUser(u.id); setNewLimit(String(u.email_limit)); }}
                            className="flex items-center gap-1 px-3 py-1.5 bg-gray-100 rounded-lg hover:bg-gold/10 text-sm font-bold text-gray-900"
                          >
                            {u.email_limit} <Edit2 className="w-3 h-3 text-gray-500" />
                          </button>
                        )}
                      </td>

                      {/* Campaigns */}
                      <td className="py-4">
                        <span className="text-sm font-bold text-gray-900">{u.campaign_count}</span>
                      </td>

                      {/* Status */}
                      <td className="py-4">
                        {u.is_blocked ? (
                          <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-bold">Blocked</span>
                        ) : (
                          <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-bold">Active</span>
                        )}
                      </td>

                      {/* Actions */}
                      <td className="py-4">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleBlock(u.id, u.is_blocked)}
                            title={u.is_blocked ? 'Unblock' : 'Block'}
                            className={`p-2 rounded-lg transition-colors ${u.is_blocked ? 'bg-green-100 hover:bg-green-200' : 'bg-red-100 hover:bg-red-200'}`}
                          >
                            {u.is_blocked ? <CheckCircle className="w-4 h-4 text-green-600" /> : <Ban className="w-4 h-4 text-red-600" />}
                          </button>
                          <button
                            onClick={() => handleResetUsage(u.id)}
                            title="Reset usage"
                            className="p-2 bg-blue-100 rounded-lg hover:bg-blue-200"
                          >
                            <RotateCcw className="w-4 h-4 text-blue-600" />
                          </button>
                          <button
                            onClick={() => handleToggleAdmin(u.id)}
                            title="Toggle admin"
                            className="p-2 bg-gold/10 rounded-lg hover:bg-gold/20"
                          >
                            <Crown className="w-4 h-4 text-gold" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Admin;
