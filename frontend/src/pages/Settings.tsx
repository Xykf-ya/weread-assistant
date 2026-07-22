import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Users, 
  RefreshCw, 
  Bell, 
  Activity,
  Plus,
  Edit2,
  Trash2,
  Check,
  Zap,
  Server,
  MessageSquare
} from 'lucide-react';
import { api } from '../services/api';
import { VintageCard } from '../components/VintageCard';
import { ACCOUNT_TYPE_MAP } from '../services/types';
import type { Account, HealthStatus, SyncResult } from '../services/types';

type TabType = 'accounts' | 'sync' | 'notifications' | 'status';

export function Settings() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>('accounts');
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<SyncResult | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingAccount, setEditingAccount] = useState<Account | null>(null);
  const [formData, setFormData] = useState({
    werss_mp_id: '',
    mp_name: '',
    cover_url: '',
    account_type: 'opportunity' as Account['account_type'],
    tags: '[]',
  });
  const [isDeleting, setIsDeleting] = useState<number | null>(null);

  useEffect(() => {
    api.accounts.getAll().then(setAccounts).catch(() => {});
    api.health.check().then(setHealth).catch(() => {});
  }, []);

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      const result = await api.sync.trigger();
      setSyncResult(result);
      api.accounts.getAll().then(setAccounts).catch(() => {});
    } catch (error) {
      console.error('同步失败:', error);
    } finally {
      setIsSyncing(false);
    }
  };

  const handleAddAccount = async () => {
    try {
      await api.accounts.create({
        werss_mp_id: formData.werss_mp_id,
        mp_name: formData.mp_name,
        cover_url: formData.cover_url || null,
        account_type: formData.account_type,
        tags: formData.tags,
      });
      setShowAddModal(false);
      setFormData({ werss_mp_id: '', mp_name: '', cover_url: '', account_type: 'opportunity', tags: '[]' });
      api.accounts.getAll().then(setAccounts).catch(() => {});
    } catch (error) {
      console.error('添加公众号失败:', error);
    }
  };

  const handleUpdateAccount = async () => {
    if (!editingAccount) return;
    try {
      await api.accounts.update(editingAccount.id, {
        mp_name: formData.mp_name,
        cover_url: formData.cover_url || null,
        account_type: formData.account_type,
        tags: formData.tags,
      });
      setShowEditModal(false);
      setEditingAccount(null);
      setFormData({ werss_mp_id: '', mp_name: '', cover_url: '', account_type: 'opportunity', tags: '[]' });
      api.accounts.getAll().then(setAccounts).catch(() => {});
    } catch (error) {
      console.error('更新公众号失败:', error);
    }
  };

  const handleDeleteAccount = async (id: number) => {
    setIsDeleting(id);
    try {
      await api.accounts.delete(id);
      api.accounts.getAll().then(setAccounts).catch(() => {});
    } catch (error) {
      console.error('删除公众号失败:', error);
    } finally {
      setIsDeleting(null);
    }
  };

  const handleTestAlert = async () => {
    try {
      await api.alerts.test();
      alert('测试通知发送成功！');
    } catch (error) {
      console.error('测试通知失败:', error);
    }
  };

  const getHealthStatus = (status: string) => {
    switch (status) {
      case 'ok':
      case 'configured':
        return { label: '已连接', color: 'text-green-600', bg: 'bg-green-100' };
      case 'auth_error':
        return { label: '认证失败', color: 'text-red-600', bg: 'bg-red-100' };
      default:
        return { label: '未知', color: 'text-amber-600', bg: 'bg-amber-100' };
    }
  };

  const tabs = [
    { id: 'accounts' as TabType, label: '公众号管理', icon: Users },
    { id: 'sync' as TabType, label: '同步管理', icon: RefreshCw },
    { id: 'notifications' as TabType, label: '通知设置', icon: Bell },
    { id: 'status' as TabType, label: '系统状态', icon: Activity },
  ];

  const renderAccountsTab = () => (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-display text-lg font-bold text-sepia-800">监控的公众号</h3>
        <button
          onClick={() => setShowAddModal(true)}
          className="vintage-btn flex items-center gap-2 text-sm"
        >
          <Plus className="w-4 h-4" />
          添加公众号
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {accounts.map((account) => (
          <VintageCard key={account.id} className="relative">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                {account.cover_url ? (
                  <img
                    src={account.cover_url}
                    alt={account.mp_name}
                    className="w-10 h-10 rounded-full object-cover"
                  />
                ) : (
                  <div className="w-10 h-10 rounded-full bg-parchment-200 flex items-center justify-center">
                    <Users className="w-5 h-5 text-sepia-400" />
                  </div>
                )}
                <div>
                  <h4 className="font-display font-semibold text-sepia-800">
                    {account.mp_name}
                  </h4>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    account.account_type === 'opportunity' ? 'bg-gold-100 text-gold-700' :
                    account.account_type === 'campus' ? 'bg-green-100 text-green-700' :
                    account.account_type === 'news' ? 'bg-gray-100 text-gray-700' :
                    'bg-orange-100 text-orange-700'
                  }`}>
                    {ACCOUNT_TYPE_MAP[account.account_type]}
                  </span>
                </div>
              </div>
              <div className={`w-2 h-2 rounded-full ${account.is_active ? 'bg-green-500' : 'bg-gray-400'}`} />
            </div>

            <div className="text-xs text-sepia-500 mb-3">
              <p>WeRSS ID: {account.werss_mp_id}</p>
              {account.tags && (
                <p>标签: {JSON.parse(account.tags).join(', ')}</p>
              )}
            </div>

            <div className="flex items-center justify-end gap-2">
              <button
                onClick={() => {
                  setEditingAccount(account);
                  setFormData({
                    werss_mp_id: account.werss_mp_id,
                    mp_name: account.mp_name,
                    cover_url: account.cover_url || '',
                    account_type: account.account_type,
                    tags: account.tags || '[]',
                  });
                  setShowEditModal(true);
                }}
                className="p-2 text-sepia-500 hover:text-sepia-700 transition-colors"
              >
                <Edit2 className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleDeleteAccount(account.id)}
                disabled={isDeleting === account.id}
                className="p-2 text-red-500 hover:text-red-700 transition-colors"
              >
                {isDeleting === account.id ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Trash2 className="w-4 h-4" />
                )}
              </button>
            </div>
          </VintageCard>
        ))}
      </div>

      {accounts.length === 0 && (
        <div className="text-center py-8 text-sepia-400">
          <Users className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>暂无公众号</p>
          <p className="text-sm mt-1">点击"添加公众号"开始监控</p>
        </div>
      )}
    </div>
  );

  const renderSyncTab = () => (
    <div>
      <h3 className="font-display text-lg font-bold text-sepia-800 mb-4">同步管理</h3>
      
      <VintageCard className="mb-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sepia-700 font-medium">手动同步</p>
            <p className="text-sm text-sepia-500">触发同步 + AI 处理流程</p>
          </div>
          <button
            onClick={handleSync}
            disabled={isSyncing}
            className="vintage-btn flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${isSyncing ? 'animate-spin' : ''}`} />
            {isSyncing ? '同步中...' : '开始同步'}
          </button>
        </div>
      </VintageCard>

      {syncResult && (
        <VintageCard>
          <h4 className="font-display font-semibold text-sepia-800 mb-3">最近同步结果</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-sepia-800">{syncResult.total_fetched}</p>
              <p className="text-xs text-sepia-500">总获取</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{syncResult.new_articles}</p>
              <p className="text-xs text-sepia-500">新文章</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{syncResult.ai_processed}</p>
              <p className="text-xs text-sepia-500">AI处理</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gold-600">{syncResult.alerts_sent}</p>
              <p className="text-xs text-sepia-500">发送通知</p>
            </div>
          </div>
          {syncResult.errors.length > 0 && (
            <div className="mt-4 pt-4 border-t border-parchment-300">
              <p className="text-sm text-red-600 mb-2">错误信息:</p>
              {syncResult.errors.map((error, index) => (
                <p key={index} className="text-xs text-sepia-500">{error}</p>
              ))}
            </div>
          )}
        </VintageCard>
      )}
    </div>
  );

  const renderNotificationsTab = () => (
    <div>
      <h3 className="font-display text-lg font-bold text-sepia-800 mb-4">通知设置</h3>
      
      <VintageCard className="mb-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sepia-700 font-medium">飞书通知</p>
            <p className="text-sm text-sepia-500">向飞书群组发送提醒</p>
          </div>
          <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${
            health?.feishu === 'configured' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'
          }`}>
            <Bell className="w-4 h-4" />
            {health?.feishu === 'configured' ? '已配置' : '未配置'}
          </div>
        </div>
      </VintageCard>

      <VintageCard>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sepia-700 font-medium">测试通知</p>
            <p className="text-sm text-sepia-500">发送测试消息验证连接</p>
          </div>
          <button
            onClick={handleTestAlert}
            className="vintage-btn flex items-center gap-2"
          >
            <MessageSquare className="w-4 h-4" />
            发送测试
          </button>
        </div>
      </VintageCard>
    </div>
  );

  const renderStatusTab = () => (
    <div>
      <h3 className="font-display text-lg font-bold text-sepia-800 mb-4">系统状态</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <VintageCard>
          <div className="flex items-center gap-3 mb-3">
            <Server className="w-8 h-8 text-sepia-600" />
            <div>
              <p className="font-display font-semibold text-sepia-800">WeRSS 服务</p>
              <p className="text-xs text-sepia-500">文章抓取</p>
            </div>
          </div>
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full w-fit ${getHealthStatus(health?.werss || '').bg}`}>
            <Check className={`w-4 h-4 ${getHealthStatus(health?.werss || '').color}`} />
            <span className={`text-sm ${getHealthStatus(health?.werss || '').color}`}>
              {getHealthStatus(health?.werss || '').label}
            </span>
          </div>
        </VintageCard>

        <VintageCard>
          <div className="flex items-center gap-3 mb-3">
            <Zap className="w-8 h-8 text-gold-500" />
            <div>
              <p className="font-display font-semibold text-sepia-800">DeepSeek AI</p>
              <p className="text-xs text-sepia-500">文本分类</p>
            </div>
          </div>
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full w-fit ${getHealthStatus(health?.deepseek || '').bg}`}>
            <Check className={`w-4 h-4 ${getHealthStatus(health?.deepseek || '').color}`} />
            <span className={`text-sm ${getHealthStatus(health?.deepseek || '').color}`}>
              {getHealthStatus(health?.deepseek || '').label}
            </span>
          </div>
        </VintageCard>

        <VintageCard>
          <div className="flex items-center gap-3 mb-3">
            <Zap className="w-8 h-8 text-purple-500" />
            <div>
              <p className="font-display font-semibold text-sepia-800">DashScope OCR</p>
              <p className="text-xs text-sepia-500">图片文章处理</p>
            </div>
          </div>
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full w-fit ${getHealthStatus(health?.dashscope || '').bg}`}>
            <Check className={`w-4 h-4 ${getHealthStatus(health?.dashscope || '').color}`} />
            <span className={`text-sm ${getHealthStatus(health?.dashscope || '').color}`}>
              {getHealthStatus(health?.dashscope || '').label}
            </span>
          </div>
        </VintageCard>

        <VintageCard>
          <div className="flex items-center gap-3 mb-3">
            <MessageSquare className="w-8 h-8 text-green-500" />
            <div>
              <p className="font-display font-semibold text-sepia-800">飞书 Webhook</p>
              <p className="text-xs text-sepia-500">通知推送</p>
            </div>
          </div>
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full w-fit ${getHealthStatus(health?.feishu || '').bg}`}>
            <Check className={`w-4 h-4 ${getHealthStatus(health?.feishu || '').color}`} />
            <span className={`text-sm ${getHealthStatus(health?.feishu || '').color}`}>
              {getHealthStatus(health?.feishu || '').label}
            </span>
          </div>
        </VintageCard>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-gradient-to-r from-sepia-900 via-sepia-800 to-sepia-900 text-parchment-50 py-4 px-6 shadow-lg">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-parchment-300 hover:text-parchment-100 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>返回看板</span>
          </button>
          <h1 className="font-display text-xl font-bold">设置管理</h1>
          <div className="w-32" />
        </div>
      </header>

      <main className="flex-1 p-6">
        <div className="max-w-5xl mx-auto">
          <div className="flex gap-1 mb-6 p-1 bg-parchment-200 rounded-sm">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-sm text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-parchment-50 text-sepia-800 shadow-sm'
                      : 'text-sepia-600 hover:text-sepia-800'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {activeTab === 'accounts' && renderAccountsTab()}
          {activeTab === 'sync' && renderSyncTab()}
          {activeTab === 'notifications' && renderNotificationsTab()}
          {activeTab === 'status' && renderStatusTab()}
        </div>
      </main>

      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-parchment-50 rounded-sm p-6 max-w-md w-full vintage-card">
            <h3 className="font-display text-lg font-bold text-sepia-800 mb-4">添加新公众号</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-sepia-700 mb-1">WeRSS MP ID</label>
                <input
                  type="text"
                  value={formData.werss_mp_id}
                  onChange={(e) => setFormData({ ...formData, werss_mp_id: e.target.value })}
                  className="w-full px-3 py-2 border border-parchment-300 rounded-sm bg-parchment-100 focus:outline-none focus:border-sepia-500"
                  placeholder="mp_abc123"
                />
              </div>
              <div>
                <label className="block text-sm text-sepia-700 mb-1">公众号名称</label>
                <input
                  type="text"
                  value={formData.mp_name}
                  onChange={(e) => setFormData({ ...formData, mp_name: e.target.value })}
                  className="w-full px-3 py-2 border border-parchment-300 rounded-sm bg-parchment-100 focus:outline-none focus:border-sepia-500"
                  placeholder="公众号名称"
                />
              </div>
              <div>
                <label className="block text-sm text-sepia-700 mb-1">公众号类型</label>
                <select
                  value={formData.account_type}
                  onChange={(e) => setFormData({ ...formData, account_type: e.target.value as Account['account_type'] })}
                  className="w-full px-3 py-2 border border-parchment-300 rounded-sm bg-parchment-100 focus:outline-none focus:border-sepia-500"
                >
                  {Object.entries(ACCOUNT_TYPE_MAP).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-sepia-700 mb-1">标签 (JSON数组)</label>
                <input
                  type="text"
                  value={formData.tags}
                  onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                  className="w-full px-3 py-2 border border-parchment-300 rounded-sm bg-parchment-100 focus:outline-none focus:border-sepia-500"
                  placeholder='["标签1", "标签2"]'
                />
              </div>
            </div>
            <div className="flex items-center justify-end gap-3 mt-6">
              <button
                onClick={() => {
                  setShowAddModal(false);
                  setFormData({ werss_mp_id: '', mp_name: '', cover_url: '', account_type: 'opportunity', tags: '[]' });
                }}
                className="px-4 py-2 text-sepia-600 hover:text-sepia-800 transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleAddAccount}
                className="vintage-btn"
              >
                添加公众号
              </button>
            </div>
          </div>
        </div>
      )}

      {showEditModal && editingAccount && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-parchment-50 rounded-sm p-6 max-w-md w-full vintage-card">
            <h3 className="font-display text-lg font-bold text-sepia-800 mb-4">编辑公众号</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-sepia-700 mb-1">WeRSS MP ID</label>
                <input
                  type="text"
                  value={formData.werss_mp_id}
                  disabled
                  className="w-full px-3 py-2 border border-parchment-300 rounded-sm bg-parchment-200 text-sepia-500"
                />
              </div>
              <div>
                <label className="block text-sm text-sepia-700 mb-1">公众号名称</label>
                <input
                  type="text"
                  value={formData.mp_name}
                  onChange={(e) => setFormData({ ...formData, mp_name: e.target.value })}
                  className="w-full px-3 py-2 border border-parchment-300 rounded-sm bg-parchment-100 focus:outline-none focus:border-sepia-500"
                />
              </div>
              <div>
                <label className="block text-sm text-sepia-700 mb-1">公众号类型</label>
                <select
                  value={formData.account_type}
                  onChange={(e) => setFormData({ ...formData, account_type: e.target.value as Account['account_type'] })}
                  className="w-full px-3 py-2 border border-parchment-300 rounded-sm bg-parchment-100 focus:outline-none focus:border-sepia-500"
                >
                  {Object.entries(ACCOUNT_TYPE_MAP).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-sepia-700 mb-1">标签 (JSON数组)</label>
                <input
                  type="text"
                  value={formData.tags}
                  onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                  className="w-full px-3 py-2 border border-parchment-300 rounded-sm bg-parchment-100 focus:outline-none focus:border-sepia-500"
                  placeholder='["标签1", "标签2"]'
                />
              </div>
            </div>
            <div className="flex items-center justify-end gap-3 mt-6">
              <button
                onClick={() => {
                  setShowEditModal(false);
                  setEditingAccount(null);
                  setFormData({ werss_mp_id: '', mp_name: '', cover_url: '', account_type: 'opportunity', tags: '[]' });
                }}
                className="px-4 py-2 text-sepia-600 hover:text-sepia-800 transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleUpdateAccount}
                className="vintage-btn"
              >
                保存修改
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
