import { useState, useEffect } from 'react';
import { Briefcase, Users, FileText } from 'lucide-react';
import { api } from '../services/api';
import { SectionHeader } from './SectionHeader';
import { VintageCard } from './VintageCard';
import { OPP_TYPE_MAP } from '../services/types';
import type { Opportunity } from '../services/types';

export function OpportunitySection() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.opportunities.getAll({ limit: 20 }).then((data) => {
      setOpportunities(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="h-full">
      <SectionHeader
        title="机会速递"
        subtitle="招聘 · 实习 · 比赛 · 训练营"
        icon={<Briefcase className="w-5 h-5 text-sepia-600" />}
        count={opportunities.length}
      />

      {loading ? (
        <div className="flex items-center justify-center h-32 text-sepia-400 text-sm">
          加载中...
        </div>
      ) : opportunities.length === 0 ? (
        <div className="text-center py-8 text-sepia-400 text-sm">
          <Briefcase className="w-10 h-10 mx-auto mb-2 opacity-50" />
          <p>暂无机会信息</p>
        </div>
      ) : (
        <div className="space-y-3">
          {opportunities.slice(0, 15).map((opp) => (
            <VintageCard
              key={opp.id}
              onClick={() => opp.original_url && window.open(opp.original_url, '_blank')}
              className="p-3"
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <span className="opp-type-tag">
                  {OPP_TYPE_MAP[opp.opp_type || 'other']}
                </span>
                {opp.deadline && (
                  <span className="date-badge">
                    {formatDate(opp.deadline)}
                  </span>
                )}
              </div>
              <h3 className="article-title text-sm leading-tight mb-2 line-clamp-2">
                {opp.opp_name || opp.title || '未命名'}
              </h3>
              <div className="flex items-center gap-3 text-xs text-sepia-500">
                <span className="flex items-center gap-1">
                  <Users className="w-3 h-3" />
                  {opp.target_audience?.slice(0, 15)}
                </span>
                {opp.mp_name && (
                  <span className="truncate max-w-[100px]">{opp.mp_name}</span>
                )}
              </div>
              {opp.requirements && (
                <p className="text-xs text-sepia-600 mt-2 line-clamp-2">
                  <FileText className="w-3 h-3 inline mr-1" />
                  {opp.requirements}
                </p>
              )}
            </VintageCard>
          ))}
          {opportunities.length > 15 && (
            <div className="text-center py-2 text-sepia-400 text-xs">
              还有 {opportunities.length - 15} 条机会信息
            </div>
          )}
        </div>
      )}
    </div>
  );
}
