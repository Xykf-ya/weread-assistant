import { useState, useEffect } from 'react';
import { Calendar, MapPin, Building2, PartyPopper, GraduationCap, Award, Heart, FileText } from 'lucide-react';
import { api } from '../services/api';
import { SectionHeader } from './SectionHeader';
import { VintageCard } from './VintageCard';
import { CAMPUS_TYPE_MAP } from '../services/types';
import type { CampusInfo } from '../services/types';

export function CampusSection() {
  const [campusInfo, setCampusInfo] = useState<CampusInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.campus.getAll({ limit: 30 }).then((data) => {
      setCampusInfo(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    if (date.toDateString() === today.toDateString()) return '今天';
    if (date.toDateString() === tomorrow.toDateString()) return '明天';
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', weekday: 'short' });
  };

  const getEventIcon = (type: string | null) => {
    switch (type) {
      case 'lecture': return <GraduationCap className="w-4 h-4" />;
      case 'competition': return <Award className="w-4 h-4" />;
      case 'volunteer': return <Heart className="w-4 h-4" />;
      case 'notice': return <FileText className="w-4 h-4" />;
      default: return <PartyPopper className="w-4 h-4" />;
    }
  };

  return (
    <div className="h-full">
      <SectionHeader
        title="校园纪事"
        subtitle="校园活动 · 讲座论坛 · 通知公告"
        icon={<Building2 className="w-5 h-5 text-green-600" />}
        count={campusInfo.length}
      />

      {loading ? (
        <div className="flex items-center justify-center h-32 text-sepia-400 text-sm">
          加载中...
        </div>
      ) : campusInfo.length === 0 ? (
        <div className="text-center py-8 text-sepia-400 text-sm">
          <Building2 className="w-10 h-10 mx-auto mb-2 opacity-50" />
          <p>暂无校园活动</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {campusInfo.slice(0, 12).map((item) => (
            <VintageCard
              key={item.id}
              onClick={() => item.original_url && window.open(item.original_url, '_blank')}
              className="p-4"
            >
              <div className="flex items-start justify-between gap-3 mb-3">
                <div className="flex items-center gap-2">
                  <span className="campus-type-tag flex items-center gap-1">
                    {getEventIcon(item.event_type)}
                    {CAMPUS_TYPE_MAP[item.event_type || 'event']}
                  </span>
                  {item.event_date && (
                    <span className="date-badge flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {formatDate(item.event_date)}
                    </span>
                  )}
                </div>
              </div>
              
              <h3 className="article-title text-base leading-tight mb-3">
                {item.title || '未命名'}
              </h3>

              <div className="space-y-2 text-xs text-sepia-600">
                {item.location && (
                  <div className="flex items-center gap-2">
                    <MapPin className="w-3 h-3 flex-shrink-0" />
                    <span>{item.location}</span>
                  </div>
                )}
                {item.organizer && (
                  <div className="flex items-center gap-2">
                    <Building2 className="w-3 h-3 flex-shrink-0" />
                    <span>{item.organizer}</span>
                  </div>
                )}
                {item.deadline && (
                  <div className="flex items-center gap-2 text-sepia-500">
                    <Calendar className="w-3 h-3 flex-shrink-0" />
                    <span>截止: {formatDate(item.deadline)}</span>
                  </div>
                )}
              </div>

              {item.mp_name && (
                <div className="mt-3 pt-2 border-t border-parchment-300">
                  <span className="text-xs text-sepia-400">来源: {item.mp_name}</span>
                </div>
              )}
            </VintageCard>
          ))}
        </div>
      )}
    </div>
  );
}
