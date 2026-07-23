import type {
  Account,
  AccountCreate,
  AccountUpdate,
  Article,
  ArticleDetail,
  Opportunity,
  OpportunityUpdate,
  CampusInfo,
  ReadingStateUpdate,
  SyncResult,
  WeRssSyncResult,
  HealthStatus,
  UpcomingOpportunity,
} from './types';

const BASE_URL = 'http://localhost:8000/api';

async function request<T>(url: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${BASE_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const data = await response.json();

  // 后端有两种响应格式：
  // 1. 带包装: {code: 0, data: [...], message: "ok"}
  // 2. 不带包装: 直接返回数组或对象
  if (data !== null && typeof data === 'object' && !Array.isArray(data) && 'code' in data) {
    if (data.code !== 0) {
      throw new Error(data.message || 'Request failed');
    }
    return data.data !== undefined ? data.data : data;
  }

  // 直接返回的数组或对象
  return data as T;
}

export const api = {
  health: {
    check: () => request<HealthStatus>('/health'),
  },
  accounts: {
    getAll: (params?: { account_type?: string; is_active?: boolean }) => {
      const query = new URLSearchParams();
      if (params?.account_type) query.set('account_type', params.account_type);
      if (params?.is_active !== undefined) query.set('is_active', String(params.is_active));
      return request<Account[]>(`/accounts?${query}`);
    },
    create: (data: AccountCreate) => request<Account>('/accounts', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: AccountUpdate) => request<Account>(`/accounts/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id: number) => request<void>(`/accounts/${id}`, { method: 'DELETE' }),
    syncFromWeRSS: () => request<WeRssSyncResult>('/accounts/sync-from-werss', { method: 'POST' }),
  },
  articles: {
    getAll: (params?: { account_type?: string; werss_mp_id?: string; limit?: number; offset?: number }) => {
      const query = new URLSearchParams();
      if (params?.account_type) query.set('account_type', params.account_type);
      if (params?.werss_mp_id) query.set('werss_mp_id', params.werss_mp_id);
      if (params?.limit) query.set('limit', String(params.limit));
      if (params?.offset) query.set('offset', String(params.offset));
      return request<Article[]>(`/articles?${query}`);
    },
    getDetail: (id: number) => request<ArticleDetail>(`/articles/${id}`),
    updateReadingState: (id: number, data: ReadingStateUpdate) => 
      request<void>(`/articles/${id}/reading-state`, { method: 'PUT', body: JSON.stringify(data) }),
  },
  opportunities: {
    getAll: (params?: { opp_type?: string; min_confidence?: number; upcoming_only?: boolean; limit?: number; offset?: number }) => {
      const query = new URLSearchParams();
      if (params?.opp_type) query.set('opp_type', params.opp_type);
      if (params?.min_confidence) query.set('min_confidence', String(params.min_confidence));
      if (params?.upcoming_only) query.set('upcoming_only', String(params.upcoming_only));
      if (params?.limit) query.set('limit', String(params.limit));
      if (params?.offset) query.set('offset', String(params.offset));
      return request<Opportunity[]>(`/opportunities?${query}`);
    },
    getUpcoming: (days?: number) => {
      const query = new URLSearchParams();
      if (days) query.set('days', String(days));
      return request<UpcomingOpportunity[]>(`/opportunities/upcoming?${query}`);
    },
    update: (id: number, data: OpportunityUpdate) => 
      request<Opportunity>(`/opportunities/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  },
  campus: {
    getAll: (params?: { event_type?: string; organizer?: string; limit?: number; offset?: number }) => {
      const query = new URLSearchParams();
      if (params?.event_type) query.set('event_type', params.event_type);
      if (params?.organizer) query.set('organizer', params.organizer);
      if (params?.limit) query.set('limit', String(params.limit));
      if (params?.offset) query.set('offset', String(params.offset));
      return request<CampusInfo[]>(`/campus?${query}`);
    },
  },
  sync: {
    trigger: () => request<SyncResult>('/sync'),
  },
  alerts: {
    test: () => request<void>('/alerts/test'),
  },
};
