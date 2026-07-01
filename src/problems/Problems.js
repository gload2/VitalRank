import { C } from '../common/colors';
import { TopBar, IssueCard } from '../common/components';
import './Problems.css';

export default function ProblemsPage({ sites, onOpenIssue, t }) {
  const all = sites.flatMap(s => [
    ...(s.googleIssues || []).map(i => ({ ...i, siteUrl: s.url })),
    ...(s.yandexIssues || []).map(i => ({ ...i, siteUrl: s.url })),
  ]);

  return (
    <div className="problems">
      <TopBar><span style={{ color: C.muted, fontSize: 18 }}>🔍</span></TopBar>

      <div className="problems__content">
        <h1 className="problems__title">{t('prob_title')}</h1>
        <p className="problems__sub">{t('prob_sub')}</p>

        {all.length === 0 ? (
          <div className="problems__empty">{t('prob_empty')}</div>
        ) : (
          all.map((issue, idx) => (
            <div key={issue.id + idx}>
              <div className="problems__site-label">{issue.siteUrl}</div>
              <IssueCard issue={issue} onClick={onOpenIssue} t={t} />
            </div>
          ))
        )}
      </div>
    </div>
  );
}
