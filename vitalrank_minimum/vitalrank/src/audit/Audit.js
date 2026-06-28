import { useState } from 'react';
import { C, scoreColor } from '../common/colors';
import { TopBar, IssueCard, Spinner, Pill } from '../common/components';
import './Audit.css';

function IssueSection({ issues, onOpenIssue, t }) {
  const quick = issues.filter(i => i.category === 'quick');
  const strat = issues.filter(i => i.category === 'strategic');
  return (
    <>
      {quick.length > 0 && (
        <div className="audit__section">
          <div className="audit__section-head">
            <span style={{ color: C.yellow }}>⚡</span>
            <span className="audit__section-label">{t('audit_quick')}</span>
          </div>
          {quick.map(i => <IssueCard key={i.id} issue={i} onClick={onOpenIssue} t={t} />)}
        </div>
      )}
      {strat.length > 0 && (
        <div className="audit__section">
          <div className="audit__section-head">
            <span style={{ color: C.dim }}>ℹ</span>
            <span className="audit__section-label">{t('audit_strategic')}</span>
          </div>
          {strat.map(i => <IssueCard key={i.id} issue={i} onClick={onOpenIssue} t={t} />)}
        </div>
      )}
    </>
  );
}

export default function AuditPage({ site, onBack, onOpenIssue, onRecheck, t }) {
  const [rechecking, setRechecking] = useState(false);
  const analyzed = typeof site.health === 'number';
  const gc = scoreColor(site.google);
  const yc = scoreColor(site.yandex);

  const handleRecheck = async () => {
    setRechecking(true);
    try { await onRecheck(); } finally { setRechecking(false); }
  };

  return (
    <div className="audit">
      <TopBar>
        <button className="audit__back-top" onClick={onBack}>
          {t('audit_back')}
        </button>
        <span style={{ color: C.muted, fontSize: 18 }}>🔍</span>
      </TopBar>

      <div className="audit__subbar">
        <div className="audit__subbar-left">
          <button className="audit__back-btn" onClick={onBack}>{t('audit_back')}</button>
          <span style={{ color: C.border }}>|</span>
          <span className="audit__site-url">{site.url}</span>
          {analyzed
            ? <Pill label={`Health ${site.health}%`} color={scoreColor(site.health)} />
            : <Pill label={t('badge_pending')} color={C.dim} />}
        </div>
        <div className="audit__subbar-right">
          <span className="audit__date">
            {t('audit_checked')} {new Date(site.addedAt).toLocaleString(t('locale'), {
              day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
            })}
          </span>
          <button
            className="audit__recheck-btn"
            onClick={handleRecheck}
            disabled={rechecking}
            style={{ opacity: rechecking ? 0.6 : 1 }}
          >
            {rechecking
              ? <><Spinner small /> {t('audit_checking')}</>
              : t('audit_recheck')}
          </button>
        </div>
      </div>

      {analyzed ? (
        <div className="audit__tracks">
          {/* Google */}
          <div>
            <div className="audit__track-head">
              <h2 className="audit__track-title" style={{ color: C.blue }}>{t('audit_google')}</h2>
              <div className="audit__track-score" style={{ color: gc, background: `${gc}22`, border: `1px solid ${gc}44` }}>
                {site.google}
              </div>
            </div>
            <IssueSection issues={site.googleIssues || []} onOpenIssue={onOpenIssue} t={t} />
          </div>

          {/* Yandex */}
          <div>
            <div className="audit__track-head">
              <h2 className="audit__track-title" style={{ color: C.red }}>{t('audit_yandex')}</h2>
              <div className="audit__track-score" style={{ color: yc, background: `${yc}22`, border: `1px solid ${yc}44` }}>
                {site.yandex}
              </div>
            </div>
            <IssueSection issues={site.yandexIssues || []} onOpenIssue={onOpenIssue} t={t} />
          </div>
        </div>
      ) : (
        <div className="audit__pending">
          <div className="audit__pending-icon">🕓</div>
          <h3 className="audit__pending-title">{t('audit_pending_title')}</h3>
          <p className="audit__pending-sub">{t('audit_pending_sub')}</p>
        </div>
      )}

      <div className="audit__footer">{t('audit_footer')}</div>
    </div>
  );
}
