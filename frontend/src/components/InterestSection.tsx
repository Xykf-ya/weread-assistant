import { useState, useEffect } from 'react';
import { Heart, Clock, Bookmark } from 'lucide-react';
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
    <div className="w-full">
      <SectionHeader
        title="兴趣精选"
        subtitle="精选文章推荐"
        icon={<Heart className="w-5 h-5 text-orange-500" />}
        count={articles.length}
      />

      {loading ? (
        <div className="flex items-center justify-center h-32 text-sepia-400 text-sm">
          加载中...
        </div>
      ) : articles.length === 0 ? (
        <div className="text-center py-8 text-sepia-400 text-sm">
          <Heart className="w-10 h-10 mx-auto mb-2 opacity-50" />
          <p>暂无精选文章</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {articles.slice(0, 15).map((article) => (
            <VintageCard
              key={article.id}
              onClick={() => window.open(article.original_url, '_blank')}
              className="p-4"
            >
              {article.cover_url && (
                <div className="w-full h-32 mb-3 rounded-sm overflow-hidden bg-parchment-200">
                  <img
                    src={article.cover_url}
                    alt={article.title}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}
              <h3 className="article-title text-sm leading-tight mb-3 line-clamp-3">
                {article.title}
              </h3>
              {article.summary && (
                <p className="text-xs text-sepia-500 mb-3 line-clamp-2">
                  {article.summary}
                </p>
              )}
              <div className="flex items-center justify-between text-xs text-sepia-400">
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {formatTime(article.published_at)}
                </span>
                <span className="flex items-center gap-1">
                  <Bookmark className="w-3 h-3" />
                  {article.author || article.mp_name}
                </span>
              </div>
            </VintageCard>
          ))}
        </div>
      )}
    </div>
  );
}
