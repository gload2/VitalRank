export const C = {
  bg:        'var(--bg)',
  surface:   'var(--surface)',
  surface2:  'var(--surface-2)',
  border:    'var(--border)',
  blue:      '#3b82f6',
  blueLight: '#60a5fa',
  red:       '#ef4444',
  orange:    '#f97316',
  green:     '#22c55e',
  yellow:    '#eab308',
  text:      'var(--text)',
  muted:     'var(--muted)',
  dim:       'var(--dim)',
};

export function scoreColor(s) {
  if (s >= 80) return C.green;
  if (s >= 60) return C.orange;
  return C.red;
}

export function badgeForSite(site, t) {
  if (site.status === 'failed') {
    return { label: t('badge_failed'), color: C.red };
  }
  if (typeof site.health !== 'number') {
    return { label: t('badge_pending'), color: C.dim };
  }
  const crit = [
    ...(site.googleIssues || []),
    ...(site.yandexIssues || []),
  ].filter(i => i.type === 'error').length;
  if (crit === 0) return { label: t('badge_healthy'), color: C.green };
  if (crit <= 3)  return { label: `${crit} ${t('badge_crit')}`, color: C.red };
  return          { label: `${crit} ${t('badge_important')}`, color: C.orange };
}
