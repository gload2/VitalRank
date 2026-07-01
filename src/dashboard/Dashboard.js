import { useState } from 'react';
import { C, scoreColor, badgeForSite } from '../common/colors';
import { TopBar } from '../common/components';
import AddSiteModal from './AddSiteModal';
import SiteRow from './SiteRow';
import './Dashboard.css';

export default function DashboardPage({ sites, onOpenSite, onAddSite, onRemoveSite, t }) {
  const [showModal, setShowModal] = useState(false);
  const [search,    setSearch]    = useState('');

  const filtered   = sites.filter(s => s.url.toLowerCase().includes(search.toLowerCase()));
  const analyzed   = sites.filter(s => typeof s.health === 'number');
  const totalCrit  = sites.reduce((acc, s) =>
    acc + [...(s.googleIssues || []), ...(s.yandexIssues || [])].filter(i => i.type === 'error').length, 0);
  const avgHealth  = analyzed.length
    ? Math.round(analyzed.reduce((a, s) => a + s.health, 0) / analyzed.length)
    : 0;

  const stats = [
    { label: t('dash_stat_sites'),   value: sites.length, sub: sites.length ? t('dash_stat_active') : null, subColor: C.blue },
    { label: t('dash_stat_checks'),  value: analyzed.length, sub: analyzed.length ? t('dash_stat_total') : null, subColor: C.muted },
    { label: t('dash_stat_crit'),    value: totalCrit, subColor: C.red,   valueColor: totalCrit > 0 ? C.red : C.text },
    { label: t('dash_stat_health'),  value: analyzed.length ? avgHealth : '—', sub: analyzed.length ? '↗' : null, subColor: C.green },
  ];

  return (
    <div className="dashboard">
      <TopBar>
        <span style={{ color: C.muted, fontSize: 18 }}>🔍</span>
      </TopBar>

      {showModal && (
        <AddSiteModal
          onClose={() => setShowModal(false)}
          onAdd={onAddSite}
          t={t}
        />
      )}

      <div className="dashboard__content">
        <div className="dashboard__head">
          <div>
            <h1 className="dashboard__title">{t('dash_title')}</h1>
            <p className="dashboard__sub">{t('dash_sub')}</p>
          </div>
          <button className="dashboard__add-btn" onClick={() => setShowModal(true)}>
            {t('dash_add')}
          </button>
        </div>

        {/* Stats */}
        <div className="dashboard__stats">
          {stats.map(s => (
            <div key={s.label} className="dashboard__stat-card">
              <div className="dashboard__stat-label">{s.label}</div>
              <div className="dashboard__stat-value" style={{ color: s.valueColor || C.text }}>
                {s.value}
              </div>
              {s.sub && (
                <div className="dashboard__stat-sub" style={{ color: s.subColor, background: `${s.subColor}22` }}>
                  {s.sub}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Empty state */}
        {sites.length === 0 ? (
          <div className="dashboard__empty">
            <div className="dashboard__empty-icon">🌐</div>
            <h3 className="dashboard__empty-title">{t('dash_empty_title')}</h3>
            <p className="dashboard__empty-sub">{t('dash_empty_sub')}</p>
            <button className="dashboard__empty-btn" onClick={() => setShowModal(true)}>
              {t('dash_empty_btn')}
            </button>
          </div>
        ) : (
          <>
            <div className="dashboard__list-head">
              <div className="dashboard__list-title">
                {t('dash_list_title')}{' '}
                <span className="dashboard__list-hint">{t('dash_list_hint')}</span>
              </div>
              <input
                className="dashboard__search"
                placeholder={t('dash_search')}
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>

            {filtered.map(site => {
              const badge = badgeForSite(site, t);
              return (
                <SiteRow
                  key={site.id}
                  site={site}
                  badge={badge}
                  gc={scoreColor(site.google)}
                  yc={scoreColor(site.yandex)}
                  onOpen={() => onOpenSite(site)}
                  onRemove={() => onRemoveSite(site.id)}
                  t={t}
                />
              );
            })}
          </>
        )}
      </div>
    </div>
  );
}
