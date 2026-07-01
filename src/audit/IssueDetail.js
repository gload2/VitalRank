import { useState } from 'react';
import { C } from '../common/colors';
import { TopBar, Pill } from '../common/components';
import { useUser } from '../common/UserContext';
import { aiFix as aiFixApi } from '../common/api';
import { translateIssue } from '../common/i18n';
import './IssueDetail.css';

export default function IssueDetailPage({ issue, onBack, t }) {
  const [copied, setCopied] = useState(false);

  const user = useUser();
  const isBusiness = user?.plan === 'business';
  const { title, desc } = translateIssue(t, issue.ruleId, issue.title, issue.desc);
  const [aiText, setAiText] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState('');
  const [aiUsedPage, setAiUsedPage] = useState(false);

  const handleAiFix = async () => {
    setAiLoading(true);
    setAiError('');
    setAiText('');
    setAiUsedPage(false);
    try {
      const res = await aiFixApi({
        title: issue.title,
        description: issue.desc,
        page_url: issue.pages?.[0],
        code_snippet: issue.fix,
      });
      setAiText(res.fix);
      setAiUsedPage(Boolean(res.used_page));
    } catch (e) {
      setAiError(e.detail || e.message || 'Ошибка');
    } finally {
      setAiLoading(false);
    }
  };

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
          <h1 className="issue-detail__title">{title}</h1>
        </div>

        <div className="issue-detail__tags">
          {tags.map(tag => <Pill key={tag.label} label={tag.label} color={tag.color} />)}
        </div>

        <div className="issue-detail__desc-box">
          <span className="issue-detail__desc-icon">ℹ</span>
          <p className="issue-detail__desc">{desc}</p>
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

        {/* AI-починка (killer-фича) — через локальный LLM, только тариф Business */}
        <div style={{ marginTop: 28 }}>
          <h3 className="issue-detail__section-title">✨ {t('issue_ai_title')}</h3>
          <p style={{ color: C.dim, fontSize: 12, marginTop: -6, marginBottom: 12 }}>
            {t('issue_ai_sub')}
          </p>
          {isBusiness ? (
            <>
              <button
                onClick={handleAiFix}
                disabled={aiLoading}
                style={{
                  background: C.blue, color: '#fff', border: 'none', borderRadius: 8,
                  padding: '10px 18px', fontSize: 14, fontWeight: 600,
                  cursor: aiLoading ? 'default' : 'pointer', opacity: aiLoading ? 0.7 : 1,
                }}
              >
                {aiLoading ? t('issue_ai_loading') : t('issue_ai_btn')}
              </button>
              {aiError && (
                <p style={{ color: C.red, fontSize: 13, marginTop: 10 }}>{aiError}</p>
              )}
              {aiText && (
                <div className="issue-detail__code-block" style={{ marginTop: 12 }}>
                  <div className="issue-detail__code-header">
                    <span className="issue-detail__code-label">
                      ✨ AI{aiUsedPage ? ` · ${t('issue_ai_analyzed')}` : ''}
                    </span>
                    <button
                      className="issue-detail__copy-btn"
                      onClick={() => navigator.clipboard.writeText(aiText).catch(() => {})}
                      style={{ color: C.muted }}
                    >
                      {t('issue_fix_copy')}
                    </button>
                  </div>
                  <pre className="issue-detail__code">{aiText}</pre>
                </div>
              )}
            </>
          ) : (
            <div style={{
              color: C.muted, fontSize: 13, padding: '12px 16px',
              border: `1px solid ${C.border}`, borderRadius: 8, background: C.surface,
            }}>
              🔒 {t('issue_ai_locked')}
            </div>
          )}
        </div>

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
