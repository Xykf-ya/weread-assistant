import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { RefreshCw, Settings, Search, BookOpen, Zap } from 'lucide-react';
import { api } from '../services/api';
import type { HealthStatus, SyncResult } from '../services/types';

interface HeaderProps {
  onSyncStart?: () => void;
  onSyncEnd?: (result: SyncResult) => void;
}

export function Header({ onSyncStart, onSyncEnd }: HeaderProps) {
  const navigate = useNavigate();
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    api.health.check().then(setHealth).catch(() => {});
    const interval = setInterval(() => {
      api.health.check().then(setHealth).catch(() => {});
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleSync = async () => {
    if (isSyncing) return;
    setIsSyncing(true);
    onSyncStart?.();
    try {
      const result = await api.sync.trigger();
      onSyncEnd?.(result);
    } catch (error) {
      console.error('同步失败:', error);
    } finally {
      setIsSyncing(false);
    }
  };

  const getHealthColor = (status: string) => {
    switch (status) {
      case 'ok': return 'text-green-600';
      case 'configured': return 'text-green-600';
      case 'auth_error': return 'text-red-500';
      default: return 'text-amber-600';
    }
  };

  return (
    <header className="vintage-texture text-parchment-50 py-4 px-6 shadow-lg">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <BookOpen className="w-8 h-8 text-gold-300" />
            <h1 className="font-display text-2xl font-bold tracking-wide text-gold-300">
              WeRead
            </h1>
          </div>
          <div className="hidden md:flex items-center gap-1 ml-4">
            <span className="text-parchment-300 text-sm font-handwriting">每日精选</span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative hidden md:block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-parchment-400" />
            <input
              type="text"
              placeholder="搜索文章..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-sepia-950/50 border border-sepia-700 rounded-lg pl-10 pr-4 py-2 text-parchment-100 text-sm placeholder:text-parchment-400 focus:outline-none focus:border-gold-400 w-64"
            />
          </div>

          <div className="hidden lg:flex items-center gap-3 text-xs text-parchment-300">
            <span className={`flex items-center gap-1 ${getHealthColor(health?.werss || 'unknown')}`}>
              <Zap className="w-3 h-3" />
              数据源
            </span>
            <span className={`flex items-center gap-1 ${getHealthColor(health?.deepseek || 'unknown')}`}>
              AI
            </span>
            <span className={`flex items-center gap-1 ${getHealthColor(health?.feishu || 'unknown')}`}>
              飞书
            </span>
          </div>

          <button
            onClick={handleSync}
            disabled={isSyncing}
            className="glass-btn-primary flex items-center gap-2 text-sm"
          >
            <RefreshCw className={`w-4 h-4 ${isSyncing ? 'animate-spin' : ''}`} />
            {isSyncing ? '同步中...' : '同步更新'}
          </button>

          <button
            onClick={() => navigate('/settings')}
            className="glass-btn-secondary flex items-center gap-2 text-sm"
          >
            <Settings className="w-4 h-4" />
            设置管理
          </button>
        </div>
      </div>
    </header>
  );
}
