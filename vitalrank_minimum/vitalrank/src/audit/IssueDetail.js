import { useState } from 'react';
import { C } from '../common/colors';
import { TopBar, Pill } from '../common/components';
import './IssueDetail.css';

export default function IssueDetailPage({ issue, onBack, t }) {
  const [copied, setCopied] = useState(false);

  const effMap    = { 'Выс': t('issue_eff_high'),    'Срд': t('issue_eff_mid'),    'Низ': t('issue_eff_low')    };
  const effortMap = { 'Выс': t('issue_effort_high'), 'Срд': t('issue_effort_mid'), 'Мин': t('issue_effort_low') };

  const tags = [
    { label: issue.type === 'error' ? t('issue_google_track') : t('issue_yandex_track'), color: C.blue },
    { label: `${t('issue_eff_label')}: ${effMap[issue.eff] || issue.eff}`,               color: C.red   },
    { label: `${t('issue_effort_label')}: ${effortMap[issue.effort] || issue.effort}`,   color: C.muted },
  ];

  const handleCopy = () => {
    navigator.clipboard.writeText(issue.fix || '').catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="issue-detail">
      <TopBar>
        <button className="issue-detail__back-btn" onClick={onBack}>
          {t('issue_back')}
        </button>
        <span style={{ color: C.muted, fontSize: 18 }}>🔍</span>
      </TopBar>

      <div className="issue-detail__body">
        <div className="issue-detail__head">
          <span
            className="issue-detail__icon"
            style={{
              background: `${issue.type === 'error' ? C.red : C.yellow}22`,
              border:     `2px solid ${issue.type === 'error' ? C.red : C.yellow}`,
              color:       issue.type === 'error' ? C.red : C.yellow,
            }}
          >
            {issue.type === 'error' ? '⊘' : '△'}
          </span>
          <h1 className="issue-detail__title">{issue.title}</h1>
        </div>

        <div className="issue-detail__tags">
          {tags.map(tag => <Pill key={tag.label} label={tag.label} color={tag.color} />)}
        </div>

        <div className="issue-detail__desc-box">
          <span className="issue-detail__desc-icon">ℹ</span>
          <p className="issue-detail__desc">{issue.desc}</p>
        </div>

        {issue.fix && (
          <div className="issue-detail__fix">
            <h3 className="issue-detail__section-title">{t('issue_fix_title')}</h3>
            <div className="issue-detail__code-block">
              <div className="issue-detail__code-header">
                <span className="issue-detail__code-label">
                  {t('issue_code')} {issue.fixLabel || t('code_default')}
                </span>
                <button
                  className="issue-detail__copy-btn"
                  onClick={handleCopy}
                  style={{ color: copied ? C.green : C.muted }}
                >
                  {copied ? t('issue_fix_copied') : t('issue_fix_copy')}
                </button>
              </div>
              <pre className="issue-detail__code">{issue.fix}</pre>
            </div>
          </div>
        )}

        {issue.pages && issue.pages.length > 0 && (
          <div className="issue-detail__pages">
            <h3 className="issue-detail__section-title">{t('issue_pages_title')}</h3>
            {issue.pages.map(p => (
              <div key={p} className="issue-detail__page-item">{p}</div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
