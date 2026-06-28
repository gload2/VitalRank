import { useState } from 'react';
import translations from './common/i18n';
import Sidebar from './common/Sidebar';
import LandingPage from './landing/Landing';
import DashboardPage from './dashboard/Dashboard';
import AuditsListPage from './audit/AuditsList';
import AuditPage from './audit/Audit';
import IssueDetailPage from './audit/IssueDetail';
import ProblemsPage from './problems/Problems';
import SettingsPage from './settings/Settings';
import './App.css';

export default function App() {
  const [view, setView] = useState('landing');
  const [page, setPage] = useState('dashboard');
  const [sites, setSites] = useState([]);
  const [selectedSite, setSelectedSite] = useState(null);
  const [selectedIssue, setSelectedIssue] = useState(null);
  const [lang, setLang] = useState('ru');

  // Переводы
  const t = (key) =>
    translations[lang]?.[key] ??
    translations['ru'][key] ??
    key;

  // Стартовая страница
  if (view === 'landing') {
    return <LandingPage onEnter={() => setView('app')} t={t} />;
  }

  // Работа с сайтами
  const addSite = (site) => {
    setSites((prev) => [...prev, site]);
  };

  const removeSite = (id) => {
    setSites((prev) => prev.filter((site) => site.id !== id));
  };

  const openSite = (site) => {
    setSelectedSite(site);
    setSelectedIssue(null);
    setPage('audit');
  };

  const openIssue = (issue) => {
    setSelectedIssue(issue);
    setPage('issue');
  };

  const backToAudit = () => {
    setSelectedIssue(null);
    setPage('audit');
  };

  const backToDashboard = () => {
    setSelectedSite(null);
    setPage('dashboard');
  };

  const navChange = (newPage) => {
    setPage(newPage);
    setSelectedSite(null);
    setSelectedIssue(null);
  };

  const signOut = () => {
    setView('landing');
    setPage('dashboard');
    setSelectedSite(null);
    setSelectedIssue(null);
  };

  // ТОЧКА ИНТЕГРАЦИИ: перепроверка сайта.
  // Сейчас бэкенд/ML не подключены — функция ничего не меняет.
  // Когда подключите анализ: запросите свежий аудит по current.url и
  // обновите сайт, сохранив форму { google, yandex, health, googleIssues, yandexIssues }.
  const recheckSite = async () => {
    // TODO: const data = await fetch(`/api/audit?url=${selectedSite.url}`).then(r => r.json());
    // setSites(prev => prev.map(s => s.id === selectedSite.id ? { ...s, ...data, status: 'done' } : s));
    // setSelectedSite(prev => ({ ...prev, ...data, status: 'done' }));
  };

  const sidebarActive =
    page === 'audit' || page === 'issue'
      ? 'audits'
      : page;

  return (
    <div className="app-layout">
      <Sidebar
        active={sidebarActive}
        onChange={navChange}
        onSignOut={signOut}
        t={t}
      />

      {page === 'dashboard' && (
        <DashboardPage
          sites={sites}
          onOpenSite={openSite}
          onAddSite={addSite}
          onRemoveSite={removeSite}
          t={t}
        />
      )}

      {page === 'audits' && !selectedSite && (
        <AuditsListPage
          sites={sites}
          onOpenSite={openSite}
          t={t}
        />
      )}

      {page === 'audit' && selectedSite && (
        <AuditPage
          site={selectedSite}
          onBack={backToDashboard}
          onOpenIssue={openIssue}
          onRecheck={recheckSite}
          t={t}
        />
      )}

      {page === 'issue' && selectedIssue && (
        <IssueDetailPage
          issue={selectedIssue}
          onBack={backToAudit}
          t={t}
        />
      )}

      {page === 'problems' && (
        <ProblemsPage
          sites={sites}
          onOpenIssue={openIssue}
          t={t}
        />
      )}

      {page === 'settings' && (
        <SettingsPage
          lang={lang}
          onLangChange={setLang}
          t={t}
        />
      )}
    </div>
  );
}