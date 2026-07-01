const BASE = process.env.REACT_APP_API_URL || '/api';

const ACCESS_KEY = 'vr_access';
const REFRESH_KEY = 'vr_refresh';

export const tokens = {
  get access() { return localStorage.getItem(ACCESS_KEY); },
  get refresh() { return localStorage.getItem(REFRESH_KEY); },
  set({ access_token, refresh_token }) {
    if (access_token) localStorage.setItem(ACCESS_KEY, access_token);
    if (refresh_token) localStorage.setItem(REFRESH_KEY, refresh_token);
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
  get isAuthed() { return Boolean(localStorage.getItem(ACCESS_KEY)); },
};

export class ApiError extends Error {
  constructor(status, detail) {
    super(detail || `Ошибка ${status}`);
    this.status = status;
    this.detail = detail;
  }
}

async function parseError(res) {
  try {
    const data = await res.json();
    if (typeof data.detail === 'string') return data.detail;
    if (Array.isArray(data.detail)) return data.detail.map((e) => e.msg).join('; ');
    return JSON.stringify(data);
  } catch {
    return `Ошибка ${res.status}`;
  }
}

async function request(path, { method = 'GET', body, form, auth = true, _retry = false } = {}) {
  const headers = {};
  const opts = { method, headers };

  if (form) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded';
    opts.body = new URLSearchParams(form).toString();
  } else if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }

  if (auth && tokens.access) {
    headers['Authorization'] = `Bearer ${tokens.access}`;
  }

  const res = await fetch(`${BASE}${path}`, opts);

  if (res.status === 401 && auth && !_retry && tokens.refresh) {
    const refreshed = await tryRefresh();
    if (refreshed) {
      return request(path, { method, body, form, auth, _retry: true });
    }
    tokens.clear();
    throw new ApiError(401, 'Сессия истекла, войдите снова');
  }

  if (!res.ok) {
    throw new ApiError(res.status, await parseError(res));
  }

  if (res.status === 204) return null;
  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

async function tryRefresh() {
  try {
    const data = await request('/auth/refresh', {
      method: 'POST',
      body: { refresh_token: tokens.refresh },
      auth: false,
    });
    tokens.set(data);
    return true;
  } catch {
    return false;
  }
}

export async function login(email, password) {
  const data = await request('/auth/login', {
    method: 'POST',
    form: { username: email, password },
    auth: false,
  });
  tokens.set(data);
  return data;
}

export async function register(email, password) {
  await request('/auth/register', {
    method: 'POST',
    body: { email, password },
    auth: false,
  });
  return login(email, password);
}

export async function me() {
  return request('/auth/me');
}

export async function getPlans() {
  return request('/account/plans');
}

export async function updatePlan(plan) {
  return request('/account/plan', { method: 'PATCH', body: { plan } });
}

export async function updateProfile(name) {
  return request('/account/profile', { method: 'PATCH', body: { name } });
}

export async function aiFix({ title, description, page_url, code_snippet }) {
  return request('/account/ai-fix', {
    method: 'POST',
    body: { title, description, page_url, code_snippet },
  });
}

export async function logout() {
  try {
    if (tokens.refresh) {
      await request('/auth/logout', { method: 'POST', body: { refresh_token: tokens.refresh }, auth: false });
    }
  } catch {
  } finally {
    tokens.clear();
  }
}

export async function createAudit(url) {
  return request('/audits', { method: 'POST', body: { url } });
}

export async function getAudit(auditId) {
  return request(`/audits/${auditId}`);
}

export async function downloadReport(auditId, filename) {
  const doFetch = () =>
    fetch(`${BASE}/audits/${auditId}/pdf`, {
      headers: tokens.access ? { Authorization: `Bearer ${tokens.access}` } : {},
    });

  let res = await doFetch();
  if (res.status === 401 && tokens.refresh && (await tryRefresh())) {
    res = await doFetch();
  }
  if (!res.ok) {
    throw new ApiError(res.status, await parseError(res));
  }

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename || `vitalrank_audit_${auditId}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export async function deleteSite(siteId) {
  return request(`/sites/${siteId}`, { method: 'DELETE' });
}

export async function loadSites() {
  const raw = await request('/sites');
  const sites = raw.map(mapSite);

  await Promise.all(
    sites.map(async (site) => {
      if (site.status === 'done' && site.latestAuditId != null) {
        try {
          const report = await getAudit(site.latestAuditId);
          const { googleIssues, yandexIssues } = mapReport(report);
          site.googleIssues = googleIssues;
          site.yandexIssues = yandexIssues;
        } catch {
        }
      }
    })
  );

  return sites;
}

function effectLabel(effect) {
  if (effect >= 7) return 'Выс';
  if (effect >= 4) return 'Срд';
  return 'Низ';
}

function effortLabel(effort) {
  if (effort >= 3) return 'Выс';
  if (effort === 2) return 'Срд';
  return 'Мин';
}

export function mapSite(s) {
  const a = s.latest_audit;
  return {
    id: s.id,
    url: s.domain || s.url,
    rawUrl: s.url,
    addedAt: s.created_at,
    status: a?.status || 'pending',
    health: a?.health_score ?? null,
    google: a?.google_score ?? null,
    yandex: a?.yandex_score ?? null,
    scoreDelta: a?.score_delta ?? null,
    error: a?.error ?? null,
    latestAuditId: a?.id ?? null,
    googleIssues: [],
    yandexIssues: [],
  };
}

export function mapReport(report) {
  const googleIssues = [];
  const yandexIssues = [];

  for (const issue of report.issues || []) {
    for (const score of issue.scores || []) {
      const mapped = {
        id: `${issue.id}-${score.engine}`,
        ruleId: issue.rule_id,
        type: score.is_critical ? 'error' : 'warning',
        category: score.bucket === 'quick_win' ? 'quick' : 'strategic',
        title: issue.title,
        desc: issue.description || issue.detail || '',
        eff: effectLabel(score.effect),
        effort: effortLabel(score.effort),
        fix: issue.code_snippet || '',
        fixLabel: issue.category || '',
        pages: issue.page_url ? [issue.page_url] : [],
      };
      (score.engine === 'yandex' ? yandexIssues : googleIssues).push(mapped);
    }
  }

  return { googleIssues, yandexIssues };
}
