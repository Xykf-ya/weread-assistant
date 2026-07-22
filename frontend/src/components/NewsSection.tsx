import { useState, useEffect } from 'react';
import { Newspaper, Clock, ExternalLink } from 'lucide-react';
import { api } from '../services/api';
import { SectionHeader } from './SectionHeader';
import type { Article } from '../services/types';

export function NewsSection() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.articles.getAll({ account_type: 'news', limit: 30 }).then((data) => {
      setArticles(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return '今天';
    if (days === 1) return '昨天';
    if (days < 7) return `${days}天前`;
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="h-full">
      <SectionHeader
        title="新闻资讯"
        subtitle="每日新闻速览"
        icon={<Newspaper className="w-5 h-5 text-gray-600" />}
        count={articles.length}
      />

      {loading ? (
        <div className="flex items-center justify-center h-32 text-sepia-400 text-sm">
          加载中...
        </div>
      ) : articles.length === 0 ? (
        <div className="text-center py-8 text-sepia-400 text-sm">
          <Newspaper className="w-10 h-10 mx-auto mb-2 opacity-50" />
          <p>暂无新闻资讯</p>
        </div>
      ) : (
        <div className="space-y-3">
          {articles.slice(0, 20).map((article) => (
            <div
              key={article.id}
              onClick={() => window.open(article.original_url, '_blank')}
              className="flex items-start gap-3 p-3 vintage-card rounded-sm cursor-pointer hover:bg-parchment-100 transition-colors"
            >
              <div className="flex-1 min-w-0">
                <h3 className="article-title text-sm leading-tight line-clamp-2 mb-1">
                  {article.title}
                </h3>
                <div className="flex items-center gap-2 text-xs text-sepia-500">
                  <span className="truncate max-w-[100px]">{article.author || article.mp_name}</span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {formatTime(article.published_at)}
                  </span>
                </div>
              </div>
              <ExternalLink className="w-4 h-4 text-sepia-400 flex-shrink-0 mt-1" />
            </div>
          ))}
          {articles.length > 20 && (
            <div className="text-center py-2 text-sepia-400 text-xs">
              还有 {articles.length - 20} 条新闻
            </div>
          )}
        </div>
      )}
    </div>
  );
}
