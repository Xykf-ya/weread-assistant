export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

export interface Account {
  id: number;
  werss_mp_id: string;
  mp_name: string;
  cover_url: string | null;
  account_type: 'opportunity' | 'campus' | 'news' | 'interest';
  tags: string | null;
  is_active: boolean;
  created_at: string;
}

export interface AccountCreate {
  werss_mp_id: string;
  mp_name: string;
  cover_url?: string | null;
  account_type?: 'opportunity' | 'campus' | 'news' | 'interest';
  tags?: string | null;
}

export interface AccountUpdate {
  mp_name?: string;
  cover_url?: string | null;
  account_type?: 'opportunity' | 'campus' | 'news' | 'interest';
  tags?: string | null;
  is_active?: boolean;
}

export interface Article {
  id: number;
  werss_article_id: string;
  werss_mp_id: string;
  title: string;
  author: string | null;
  summary: string | null;
  cover_url: string | null;
  original_url: string;
  published_at: string;
  fetched_at: string;
  ai_processed: boolean;
  mp_name?: string | null;
}

export interface ArticleDetail extends Article {
  raw_content: string | null;
}

export interface Opportunity {
  id: number;
  article_id: number;
  is_opportunity: boolean;
  confidence: number | null;
  opp_type: 'job' | 'internship' | 'competition' | 'camp' | 'volunteer' | 'registration' | 'other' | null;
  opp_name: string | null;
  deadline: string | null;
  deadline_display: string | null;
  target_audience: string | null;
  requirements: string | null;
  notified: boolean;
  processed_at: string;
  title: string | null;
  mp_name: string | null;
  original_url: string | null;
  published_at: string | null;
}

export interface OpportunityUpdate {
  is_opportunity?: boolean;
  opp_type?: 'job' | 'internship' | 'competition' | 'camp' | 'volunteer' | 'registration' | 'other';
  opp_name?: string;
  deadline?: string;
  deadline_display?: string;
  target_audience?: string;
  requirements?: string;
}

export interface CampusInfo {
  id: number;
  article_id: number;
  event_type: 'event' | 'lecture' | 'competition' | 'volunteer' | 'internship' | 'notice' | null;
  event_date: string | null;
  location: string | null;
  organizer: string | null;
  deadline: string | null;
  processed_at: string;
  title: string | null;
  mp_name: string | null;
  original_url: string | null;
  published_at: string | null;
}

export interface ReadingStateUpdate {
  is_read?: boolean;
  is_favorite?: boolean;
  notes?: string;
}

export interface WeRssSyncResult {
  code: number;
  message: string;
  added: number;
  skipped: number;
  added_names: string[];
  skipped_names: string[];
}

export interface SyncResult {
  total_fetched: number;
  new_articles: number;
  ai_processed: number;
  alerts_sent: number;
  errors: string[];
}

export interface HealthStatus {
  status: string;
  werss: string;
  deepseek: string;
  dashscope: string;
  feishu: string;
}

export interface UpcomingOpportunity {
  id: number;
  opp_name: string;
  opp_type: string;
  deadline: string;
  days_left: number;
  mp_name: string;
  original_url: string;
}

export const OPP_TYPE_MAP: Record<string, string> = {
  job: '招聘',
  internship: '实习',
  competition: '比赛',
  camp: '训练营',
  volunteer: '志愿',
  registration: '报名',
  other: '其他',
};

export const CAMPUS_TYPE_MAP: Record<string, string> = {
  event: '活动',
  lecture: '讲座',
  competition: '比赛',
  volunteer: '志愿',
  internship: '实习',
  notice: '通知',
};

export const ACCOUNT_TYPE_MAP: Record<string, string> = {
  opportunity: '机会类',
  campus: '校园类',
  news: '新闻类',
  interest: '兴趣类',
};
