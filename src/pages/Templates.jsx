import { 
  FileText, Plus, Edit2, Trash2, Eye, Copy, 
  Mail, Code, Clock, Loader2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import Textarea from '../components/Textarea';
import Modal from '../components/Modal';
import { useState, useEffect } from 'react';
import { useToast } from '../components/Toast';

const Templates = () => {
  const { addToast } = useToast();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [previewTemplate, setPreviewTemplate] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    subject: '',
    body: '',
    category: 'General'
  });

  // Fetch templates from backend
  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/templates/');
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates || []);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
      setTimeout(() => {
        addToast('Failed to load templates', 'error');
      }, 0);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!formData.name || !formData.subject || !formData.body) {
      setTimeout(() => {
        addToast('Please fill all fields', 'error');
      }, 0);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/v1/templates/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setTimeout(() => {
          addToast('Template created successfully!', 'success');
        }, 0);
        setShowCreateModal(false);
        setFormData({ name: '', subject: '', body: '', category: 'General' });
        fetchTemplates();
      }
    } catch (error) {
      console.error('Error creating template:', error);
      setTimeout(() => {
        addToast('Failed to create template', 'error');
      }, 0);
    }
  };

  const handleUpdate = async () => {
    if (!formData.name || !formData.subject || !formData.body) {
      setTimeout(() => {
        addToast('Please fill all fields', 'error');
      }, 0);
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/v1/templates/${editingTemplate.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setTimeout(() => {
          addToast('Template updated successfully!', 'success');
        }, 0);
        setShowCreateModal(false);
        setEditingTemplate(null);
        setFormData({ name: '', subject: '', body: '', category: 'General' });
        fetchTemplates();
      }
    } catch (error) {
      console.error('Error updating template:', error);
      setTimeout(() => {
        addToast('Failed to update template', 'error');
      }, 0);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this template?')) return;

    try {
      const response = await fetch(`http://localhost:8000/api/v1/templates/${id}`, {
        method: 'DELETE'
      });

      if (response.ok || response.status === 204) {
        setTimeout(() => {
          addToast('Template deleted successfully!', 'success');
        }, 0);
        fetchTemplates();
      }
    } catch (error) {
      console.error('Error deleting template:', error);
      setTimeout(() => {
        addToast('Failed to delete template', 'error');
      }, 0);
    }
  };

  const handleEdit = (template) => {
    setEditingTemplate(template);
    setFormData({
      name: template.name,
      subject: template.subject,
      body: template.body,
      category: template.category || 'General'
    });
    setShowCreateModal(true);
  };

  const handleDuplicate = (template) => {
    setFormData({
      name: `${template.name} (Copy)`,
      subject: template.subject,
      body: template.body,
      category: template.category || 'General'
    });
    setShowCreateModal(true);
  };

  const handlePreview = (template) => {
    setPreviewTemplate(template);
    setShowPreviewModal(true);
  };

  const insertTag = (tag) => {
    setFormData(prev => ({
      ...prev,
      body: prev.body + tag
    }));
  };

  // Personalization tags
  const tags = [
    { label: '{first_name}', value: '{first_name}', description: 'Recipient first name' },
    { label: '{last_name}', value: '{last_name}', description: 'Recipient last name' },
    { label: '{email}', value: '{email}', description: 'Recipient email' }
  ];

  // Category colors
  const categoryColors = {
    'General': { color: 'from-gray-500 to-gray-600', bgColor: 'bg-gray-500/10' },
    'Onboarding': { color: 'from-blue-500 to-blue-600', bgColor: 'bg-blue-500/10' },
    'Newsletter': { color: 'from-green-500 to-green-600', bgColor: 'bg-green-500/10' },
    'Marketing': { color: 'from-purple-500 to-purple-600', bgColor: 'bg-purple-500/10' },
    'Transactional': { color: 'from-red-500 to-red-600', bgColor: 'bg-red-500/10' },
    'E-commerce': { color: 'from-gold to-gold-light', bgColor: 'bg-gold/10' }
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
            <FileText className="w-9 h-9 text-white" />
          </div>
          <div>
            <h2 className="text-4xl font-black text-gray-900">Email Templates</h2>
            <p className="text-lg font-bold text-gray-700">Manage your email templates and designs</p>
          </div>
        </div>
        <Button
          icon={Plus}
          onClick={() => {
            setEditingTemplate(null);
            setFormData({ name: '', subject: '', body: '', category: 'General' });
            setShowCreateModal(true);
          }}
        >
          Create Template
        </Button>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <Card>
          <div className="flex items-center gap-3">
            <div className="p-4 bg-blue-100 rounded-xl shadow-md">
              <FileText className="w-7 h-7 text-blue-600" />
            </div>
            <div>
              <p className="text-base font-bold text-gray-700">Total Templates</p>
              <h3 className="text-3xl font-black text-gray-900">{templates.length}</h3>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="p-4 bg-green-100 rounded-xl shadow-md">
              <Mail className="w-7 h-7 text-green-600" />
            </div>
            <div>
              <p className="text-base font-bold text-gray-700">Total Usage</p>
              <h3 className="text-3xl font-black text-gray-900">
                {templates.reduce((sum, t) => sum + (t.usage_count || 0), 0).toLocaleString()}
              </h3>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="p-4 bg-purple-100 rounded-xl shadow-md">
              <Code className="w-7 h-7 text-purple-600" />
            </div>
            <div>
              <p className="text-base font-bold text-gray-700">Categories</p>
              <h3 className="text-3xl font-black text-gray-900">
                {new Set(templates.map(t => t.category)).size}
              </h3>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="p-4 bg-gold/20 rounded-xl shadow-md">
              <Clock className="w-7 h-7 text-gold" />
            </div>
            <div>
              <p className="text-base font-bold text-gray-700">Most Used</p>
              <h3 className="text-xl font-black text-gray-900 truncate">
                {templates.length > 0 
                  ? templates.reduce((max, t) => t.usage_count > max.usage_count ? t : max, templates[0]).name 
                  : 'N/A'}
              </h3>
            </div>
          </div>
        </Card>
      </div>

      {/* Templates Grid */}
      {templates.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <FileText className="w-20 h-20 text-gray-400 mx-auto mb-4" />
            <h3 className="text-2xl font-black text-gray-900 mb-2">No templates yet</h3>
            <p className="text-lg font-bold text-gray-700 mb-4">Create your first email template to get started</p>
            <Button
              icon={Plus}
              onClick={() => {
                setEditingTemplate(null);
                setFormData({ name: '', subject: '', body: '', category: 'General' });
                setShowCreateModal(true);
              }}
            >
              Create Template
            </Button>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AnimatePresence mode="popLayout">
            {templates.map((template, index) => {
              const colors = categoryColors[template.category] || categoryColors['General'];
              
              return (
                <motion.div
                  key={template.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ delay: index * 0.05 }}
                  layout
                >
                  <Card hover className="h-full flex flex-col">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className={`${colors.bgColor} p-4 rounded-xl shadow-md`}>
                        <Mail className={`w-7 h-7 ${colors.color.replace('from-', 'text-').replace(' to-', '').split(' ')[0]}`} />
                      </div>
                      <span className="text-xs font-bold text-gray-600 px-3 py-1.5 bg-gray-100 rounded-full">
                        {template.category || 'General'}
                      </span>
                    </div>

                    {/* Content */}
                    <div className="flex-1">
                      <h3 className="text-xl font-black text-gray-900 mb-2">{template.name}</h3>
                      <p className="text-sm font-bold text-gray-700 mb-1">
                        <span className="font-black">Subject:</span> {template.subject}
                      </p>
                      <p className="text-xs font-semibold text-gray-600 line-clamp-3 mb-3">
                        {template.body.substring(0, 100)}...
                      </p>
                    </div>

                    {/* Footer */}
                    <div className="flex items-center justify-between pt-4 border-t-2 border-gray-200">
                      <div className="flex items-center gap-2 text-xs font-bold text-gray-600">
                        <Mail className="w-5 h-5" />
                        <span>{template.usage_count || 0} uses</span>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handlePreview(template)}
                          className="p-2.5 text-blue-600 hover:bg-blue-100 rounded-xl transition-colors shadow-sm"
                          title="Preview"
                        >
                          <Eye className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handleEdit(template)}
                          className="p-2.5 text-gold hover:bg-gold/10 rounded-xl transition-colors shadow-sm"
                          title="Edit"
                        >
                          <Edit2 className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handleDuplicate(template)}
                          className="p-2.5 text-green-600 hover:bg-green-100 rounded-xl transition-colors shadow-sm"
                          title="Duplicate"
                        >
                          <Copy className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handleDelete(template.id)}
                          className="p-2.5 text-red-600 hover:bg-red-100 rounded-xl transition-colors shadow-sm"
                          title="Delete"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  </Card>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      )}

      {/* Create/Edit Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false);
          setEditingTemplate(null);
          setFormData({ name: '', subject: '', body: '', category: 'General' });
        }}
        title={editingTemplate ? 'Edit Template' : 'Create New Template'}
      >
        <div className="space-y-4">
          <Input
            label="Template Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g. Welcome Email"
          />

          <div>
            <label className="block text-base font-bold text-gray-700 mb-2">
              Category
            </label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-300 rounded-xl text-gray-900 font-bold focus:outline-none focus:border-gold transition-colors shadow-sm"
            >
              <option value="General">General</option>
              <option value="Onboarding">Onboarding</option>
              <option value="Newsletter">Newsletter</option>
              <option value="Marketing">Marketing</option>
              <option value="Transactional">Transactional</option>
              <option value="E-commerce">E-commerce</option>
            </select>
          </div>

          <Input
            label="Subject Line"
            value={formData.subject}
            onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
            placeholder="e.g. Welcome {first_name}!"
          />

          <div>
            <label className="block text-base font-bold text-gray-700 mb-2">
              Personalization Tags
            </label>
            <div className="flex flex-wrap gap-2 mb-2">
              {tags.map(tag => (
                <button
                  key={tag.value}
                  onClick={() => insertTag(tag.value)}
                  className="px-4 py-2 bg-gold/10 text-gold font-bold rounded-xl text-sm hover:bg-gold/20 transition-colors border-2 border-gold/30 shadow-sm"
                  title={tag.description}
                >
                  {tag.label}
                </button>
              ))}
            </div>
          </div>

          <Textarea
            label="Email Body"
            value={formData.body}
            onChange={(e) => setFormData({ ...formData, body: e.target.value })}
            placeholder="Hi {first_name},&#10;&#10;Welcome to our platform!&#10;&#10;Best regards"
            rows={10}
          />

          <div className="flex justify-end gap-3 pt-4">
            <Button
              variant="secondary"
              onClick={() => {
                setShowCreateModal(false);
                setEditingTemplate(null);
                setFormData({ name: '', subject: '', body: '', category: 'General' });
              }}
            >
              Cancel
            </Button>
            <Button onClick={editingTemplate ? handleUpdate : handleCreate}>
              {editingTemplate ? 'Update' : 'Create'} Template
            </Button>
          </div>
        </div>
      </Modal>

      {/* Preview Modal */}
      <Modal
        isOpen={showPreviewModal}
        onClose={() => {
          setShowPreviewModal(false);
          setPreviewTemplate(null);
        }}
        title="Template Preview"
      >
        {previewTemplate && (
          <div className="space-y-4">
            <div>
              <p className="text-base font-bold text-gray-700 mb-2">Subject:</p>
              <p className="text-gray-900 font-black text-lg">{previewTemplate.subject}</p>
            </div>
            <div>
              <p className="text-base font-bold text-gray-700 mb-2">Body:</p>
              <div className="bg-gray-50 p-5 rounded-xl text-gray-900 font-semibold whitespace-pre-wrap border-2 border-gray-300 shadow-inner">
                {previewTemplate.body}
              </div>
            </div>
            <div className="flex justify-end pt-4">
              <Button onClick={() => setShowPreviewModal(false)}>
                Close
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Templates;
