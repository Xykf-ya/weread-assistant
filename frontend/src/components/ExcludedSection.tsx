import { useState, useEffect } from 'react';
import { EyeOff, ChevronDown, ChevronUp } from 'lucide-react';
import { SectionHeader } from './SectionHeader';
import { VintageCard } from './VintageCard';

interface ExcludedItem {
  title: string;
  mp_name: string;
  published_at: string;
  verdict: string;
  original_url: string;
}

interface ExcludedData {
  total: number;
  results: ExcludedItem[];
}

export function ExcludedSection() {
  const [expanded, setExpanded] = useState(false);
  const [opportunityExcluded, setOpportunityExcluded] = useState<ExcludedData | null>(null);
  const [campusExcluded, setCampusExcluded] = useState<ExcludedData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch('/api/debug/ai-results?task_type=opportunity').then(r => r.json()),
      fetch('/api/debug/ai-results?task_type=campus').then(r => r.json()),
    ]).then(([opp, cam]) => {
      // 只保留被排除的
      setOpportunityExcluded({
        total: opp.results.filter((i: ExcludedItem) => i.verdict.includes('非机会')).length,
        results: opp.results.filter((i: ExcludedItem) => i.verdict.includes('非机会')),
      });
      setCampusExcluded({
        total: cam.results.filter((i: ExcludedItem) => i.verdict.includes('非活动') || i.verdict.includes('无分类')).length,
        results: cam.results.filter((i: ExcludedItem) => i.verdict.includes('非活动') || i.verdict.includes('无分类')),
      });
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const totalExcluded = (opportunityExcluded?.total || 0) + (campusExcluded?.total || 0);

  if (loading || totalExcluded === 0) return null;

  return (
    <div className="mt-6">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-sm text-sepia-500 hover:text-sepia-700 transition-colors mb-3"
      >
        <EyeOff className="w-4 h-4" />
        <span>已过滤 {totalExcluded} 篇文章（点击展开查看）</span>
        {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {expanded && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* 机会类排除 */}
          {opportunityExcluded && opportunityExcluded.results.length > 0 && (
            <div>
              <SectionHeader
                title="机会类已排除"
                subtitle={`${opportunityExcluded.total} 篇被判定为非机会`}
                icon={<EyeOff className="w-4 h-4 text-amber-500" />}
                count={opportunityExcluded.total}
              />
              <div className="space-y-2 mt-2 max-h-80 overflow-y-auto">
                {opportunityExcluded.results.map((item, i) => (
                  <VintageCard
                    key={i}
                    onClick={() => window.open(item.original_url, '_blank')}
                    className="p-2 text-xs"
                  >
                    <p className="line-clamp-2 text-sepia-700">{item.title}</p>
                    <p className="text-sepia-400 mt-1">{item.mp_name} · {item.published_at?.slice(0, 10)}</p>
                  </VintageCard>
                ))}
              </div>
            </div>
          )}

          {/* 校园类排除 */}
          {campusExcluded && campusExcluded.results.length > 0 && (
            <div>
              <SectionHeader
                title="校园类已排除"
                subtitle={`${campusExcluded.total} 篇被判定为新闻/无分类`}
                icon={<EyeOff className="w-4 h-4 text-gray-500" />}
                count={campusExcluded.total}
              />
              <div className="space-y-2 mt-2 max-h-80 overflow-y-auto">
                {campusExcluded.results.map((item, i) => (
                  <VintageCard
                    key={i}
                    onClick={() => window.open(item.original_url, '_blank')}
                    className="p-2 text-xs"
                  >
                    <p className="line-clamp-2 text-sepia-700">{item.title}</p>
                    <p className="text-sepia-400 mt-1">{item.mp_name} · {item.published_at?.slice(0, 10)}</p>
                  </VintageCard>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
