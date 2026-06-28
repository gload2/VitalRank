import { useState } from 'react';
import { C, scoreColor, badgeForSite } from '../common/colors';
import { TopBar, ScoreRing, Pill } from '../common/components';
import './AuditsList.css';

export default function AuditsListPage({ sites, onOpenSite, t }) {
  return (
    <div className="audits-list">
      <TopBar><span style={{ color: C.muted, fontSize: 18 }}>🔍</span></TopBar>

      <div className="audits-list__content">
        <h1 className="audits-list__title">{t('audits_title')}</h1>
        <p className="audits-list__sub">{t('audits_sub')}</p>

        {sites.length === 0 ? (
          <div className="audits-list__empty">{t('audits_empty')}</div>
        ) : (
          sites.map(site => <AuditRow key={site.id} site={site} onOpen={() => onOpenSite(site)} t={t} />)
        )}
      </div>
    </div>
  );
}

function AuditRow({ site, onOpen, t }) {
  const [hover, setHover] = useState(false);
  const badge = badgeForSite(site, t);
  return (
    <div
      className={`audit-row${hover ? ' audit-row--hover' : ''}`}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      onClick={onOpen}
    >
      <ScoreRing score={site.health} />
      <div className="audit-row__info">
        <div className="audit-row__url">{site.url}</div>
        <div className="audit-row__count">
          {typeof site.health === 'number'
            ? `${(site.googleIssues?.length || 0) + (site.yandexIssues?.length || 0)} ${t('audits_problems')}`
            : t('badge_pending')}
        </div>
      </div>
      <Pill label={badge.label} color={badge.color} />
      <span className="audit-row__open">{t('audits_open')}</span>
    </div>
  );
}
