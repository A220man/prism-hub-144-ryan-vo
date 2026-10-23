// Prompts Page
import { useEffect, useState } from 'react';
import { api, type Prompt, type PromptCreate, type PromptListResponse } from '../api';
import { Modal } from '../components/Modal';
import { useToast } from '../components/Toast';

interface PromptFormData {
  model_name: string;
  prompt_text: string;
  is_default: boolean;
  tags: string;
}

export function PromptsPage() {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [search, setSearch] = useState('');
  const [modelFilter, setModelFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null);
  const [formData, setFormData] = useState<PromptFormData>({
    model_name: '',
    prompt_text: '',
    is_default: false,
    tags: '',
  });
  const { showToast } = useToast();

  const fetchPrompts = async () => {
    setLoading(true);
    setError(null);
    try {
      const response: PromptListResponse = await api.listPrompts({
        page,
        page_size: pageSize,
        model_name: modelFilter || undefined,
        search: search || undefined,
      });
      setPrompts(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch prompts');
      showToast('Failed to load prompts', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrompts();
  }, [page, modelFilter, search]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingPrompt) {
        await api.updatePrompt(editingPrompt.id, formData);
        showToast('Prompt updated', 'success');
      } else {
        await api.createPrompt(formData);
        showToast('Prompt created', 'success');
      }
      setShowModal(false);
      setEditingPrompt(null);
      resetForm();
      fetchPrompts();
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Operation failed', 'error');
    }
  };

  const resetForm = () => {
    setFormData({ model_name: '', prompt_text: '', is_default: false, tags: '' });
  };

  const openCreateModal = () => {
    resetForm();
    setEditingPrompt(null);
    setShowModal(true);
  };

  const openEditModal = (prompt: Prompt) => {
    setFormData({
      model_name: prompt.model_name,
      prompt_text: prompt.prompt_text,
      is_default: prompt.is_default,
      tags: prompt.tags,
    });
    setEditingPrompt(prompt);
    setShowModal(true);
  };

  const handleDelete = async (prompt: Prompt) => {
    if (!window.confirm(`Delete prompt for "${prompt.model_name}"?`)) return;
    try {
      await api.deletePrompt(prompt.id);
      showToast('Prompt deleted', 'success');
      fetchPrompts();
    } catch (err) {
      showToast('Failed to delete prompt', 'error');
    }
  };

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const text = await file.text();
      const data: PromptCreate[] = JSON.parse(text);
      await api.importPrompts(data);
      showToast(`Imported ${data.length} prompts`, 'success');
      fetchPrompts();
    } catch (err) {
      showToast('Invalid JSON file', 'error');
    }
    e.target.value = '';
  };

  const handleExport = async () => {
    try {
      const data = await api.exportPrompts(modelFilter || undefined);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `prompts-${modelFilter || 'all'}-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
      showToast(`Exported ${data.length} prompts`, 'success');
    } catch (err) {
      showToast('Export failed', 'error');
    }
  };

  if (loading && prompts.length === 0) {
    return <div className="flex justify-center py-12"><div className="spinner" /></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text)]">Prompts</h1>
          <p className="text-[var(--color-text-muted)]">Manage jailbreak prompts per model</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button className="btn btn-primary" onClick={openCreateModal}>Add Prompt</button>
          <button className="btn btn-outline" onClick={handleExport}>Export JSON</button>
          <label className="btn btn-outline cursor-pointer">
            Import JSON
            <input type="file" accept=".json" onChange={handleImport} className="hidden" />
          </label>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-4 flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <label className="label">Search</label>
          <input
            type="text"
            className="input"
            placeholder="Search prompts..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
        </div>
        <div className="w-full sm:w-64">
          <label className="label">Model Filter</label>
          <input
            type="text"
            className="input"
            placeholder="Filter by model..."
            value={modelFilter}
            onChange={(e) => { setModelFilter(e.target.value); setPage(1); }}
          />
        </div>
      </div>

      {/* Table */}
      <div className="card">
        {error && <div className="alert alert-error p-4 m-4">{error}</div>}

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Model</th>
                <th>Prompt</th>
                <th>Default</th>
                <th>Tags</th>
                <th>Created</th>
                <th className="w-32">Actions</th>
              </tr>
            </thead>
            <tbody>
              {prompts.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-[var(--color-text-muted)]">
                    No prompts found. Click "Add Prompt" to create one.
                  </td>
                </tr>
              ) : (
                prompts.map((prompt) => (
                  <tr key={prompt.id}>
                    <td className="font-mono text-sm">{prompt.model_name}</td>
                    <td className="max-w-xs truncate" title={prompt.prompt_text}>{prompt.prompt_text}</td>
                    <td>
                      {prompt.is_default && <span className="badge badge-default">Default</span>}
                    </td>
                    <td className="text-sm text-[var(--color-text-muted)]">{prompt.tags || '—'}</td>
                    <td className="text-sm text-[var(--color-text-muted)]">
                      {new Date(prompt.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <div className="flex items-center gap-2">
                        <button
                          className="btn btn-outline btn-sm"
                          onClick={() => openEditModal(prompt)}
                          aria-label={`Edit prompt for ${prompt.model_name}`}
                        >
                          Edit
                        </button>
                        <button
                          className="btn btn-outline btn-sm btn-danger"
                          onClick={() => handleDelete(prompt)}
                          aria-label={`Delete prompt for ${prompt.model_name}`}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between p-4 border-t border-[var(--color-border)]">
            <p className="text-sm text-[var(--color-text-muted)]">
              Page {page} of {totalPages} — {total} total
            </p>
            <div className="flex gap-2">
              <button
                className="btn btn-outline btn-sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                Previous
              </button>
              <button
                className="btn btn-outline btn-sm"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modal */}
      <Modal
        isOpen={showModal}
        onClose={() => { setShowModal(false); setEditingPrompt(null); }}
        title={editingPrompt ? 'Edit Prompt' : 'Create Prompt'}
        footer={
          <div className="flex justify-end gap-3">
            <button className="btn btn-outline" onClick={() => { setShowModal(false); setEditingPrompt(null); }}>
              Cancel
            </button>
            <button className="btn btn-primary" onClick={handleSubmit}>
              {editingPrompt ? 'Update' : 'Create'}
            </button>
          </div>
        }
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label" htmlFor="model_name">Model Name *</label>
            <input
              id="model_name"
              type="text"
              className="input"
              placeholder="e.g., gpt-4, claude-3, xiaoma-la"
              value={formData.model_name}
              onChange={(e) => setFormData({ ...formData, model_name: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="label" htmlFor="prompt_text">Prompt Text *</label>
            <textarea
              id="prompt_text"
              className="input"
              rows={6}
              placeholder="Enter the jailbreak prompt..."
              value={formData.prompt_text}
              onChange={(e) => setFormData({ ...formData, prompt_text: e.target.value })}
              required
            />
          </div>
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_default}
                onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
              />
              <span>Set as default for this model</span>
            </label>
          </div>
          <div>
            <label className="label" htmlFor="tags">Tags (comma-separated)</label>
            <input
              id="tags"
              type="text"
              className="input"
              placeholder="jailbreak, chinese, test"
              value={formData.tags}
              onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
            />
          </div>
        </form>
      </Modal>
    </div>
  );
}