import { useState, useEffect } from 'react';
import { Heart, Clock } from 'lucide-react';
import { api } from '../services/api';
import { SectionHeader } from './SectionHeader';
import { VintageCard } from './VintageCard';
import type { Article } from '../services/types';

export function InterestSection() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.articles.getAll({ account_type: 'interest', limit: 50 }).then((data) => {
      setArticles(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="h-full">
      <SectionHeader
        title="兴趣必读"
        subtitle="每篇都值得一看"
        icon={<Heart className="w-5 h-5 text-sepia-600" />}
        count={articles.length}
      />

      {loading ? (
        <div className="flex items-center justify-center h-32 text-sepia-400 text-sm">
          加载中...
        </div>
      ) : articles.length === 0 ? (
        <div className="text-center py-8 text-sepia-400 text-sm">
          <Heart className="w-10 h-10 mx-auto mb-2 opacity-50" />
          <p>暂无文章</p>
        </div>
      ) : (
        <div className="space-y-3">
          {articles.slice(0, 15).map((article) => (
            <VintageCard
              key={article.id}
              onClick={() => window.open(article.original_url, '_blank')}
              className="p-3"
            >
              <div className="flex items-start gap-3">
                {article.cover_url && (
                  <img
                    src={article.cover_url}
                    alt={article.title}
                    className="w-14 h-10 object-cover rounded-sm flex-shrink-0"
                  />
                )}
                <div className="flex-1 min-w-0">
                  <h3 className="article-title text-sm leading-tight mb-1 line-clamp-2">
                    {article.title}
                  </h3>
                  <div className="flex items-center gap-2 text-xs text-sepia-400">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatTime(article.published_at)}
                    </span>
                    {article.mp_name && (
                      <span className="truncate">{article.mp_name}</span>
                    )}
                  </div>
                </div>
              </div>
            </VintageCard>
          ))}
          {articles.length > 15 && (
            <div className="text-center py-2 text-sepia-400 text-xs">
              还有 {articles.length - 15} 篇
            </div>
          )}
        </div>
      )}
    </div>
  );
}
