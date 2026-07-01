import { useState, useEffect, useCallback } from 'react';
import translations from './common/i18n';
import * as api from './common/api';
import Sidebar from './common/Sidebar';
import LandingPage from './landing/Landing';
import AuthPage from './auth/AuthPage';
import DashboardPage from './dashboard/Dashboard';
import AuditsListPage from './audit/AuditsList';
import AuditPage from './audit/Audit';
import IssueDetailPage from './audit/IssueDetail';
import ProblemsPage from './problems/Problems';
import SettingsPage from './settings/Settings';
import { UserContext } from './common/UserContext';
import './App.css';

export default function App() {
  const [view, setView] = useState('landing');
  const [booting, setBooting] = useState(true);
  const [user, setUser] = useState(null);

  const [page, setPage] = useState('dashboard');
  const [sites, setSites] = useState([]);
  const [selectedSiteId, setSelectedSiteId] = useState(null);
  const [selectedIssue, setSelectedIssue] = useState(null);
  const [lang, setLang] = useState('ru');

  const t = (key) =>
    translations[lang]?.[key] ??
    translations['ru'][key] ??
    key;

  const reloadSites = useCallback(async () => {
    const list = await api.loadSites();
    setSites(list);
  }, []);

  useEffect(() => {
    let active = true;
    (async () => {
      if (!api.tokens.isAuthed) {
        if (active) setBooting(false);
        return;
      }
      try {
        const me = await api.me();
        if (!active) return;
        setUser(me);
        await reloadSites();
        if (!active) return;
        setView('app');
      } catch {
        api.tokens.clear();
      } finally {
        if (active) setBooting(false);
      }
    })();
    return () => { active = false; };
  }, [reloadSites]);

  const hasPending = sites.some((s) => s.status === 'pending' || s.status === 'processing');
  useEffect(() => {
    if (view !== 'app' || !hasPending) return undefined;
    const id = setInterval(() => { reloadSites().catch(() => {}); }, 3000);
    return () => clearInterval(id);
  }, [view, hasPending, reloadSites]);

  const selectedSite = sites.find((s) => s.id === selectedSiteId) || null;

  if (booting) {
    return <div style={{ minHeight: '100vh', background: 'var(--bg)' }} />;
  }

  if (view === 'landing') {
    return <LandingPage onEnter={() => setView('auth')} t={t} />;
  }

  if (view === 'auth') {
    return (
      <AuthPage
        onBack={() => setView('landing')}
        onSuccess={async (me) => {
          setUser(me);
          try { await reloadSites(); } catch { /* пусто — покажем дашборд без сайтов */ }
          setPage('dashboard');
          setView('app');
        }}
        t={t}
      />
    );
  }

  const addSite = async (url) => {
    const full = /^https?:\/\//i.test(url) ? url : `https://${url}`;
    await api.createAudit(full);
    await reloadSites();
  };

  const removeSite = async (id) => {
    await api.deleteSite(id);
    setSites((prev) => prev.filter((site) => site.id !== id));
    if (selectedSiteId === id) {
      setSelectedSiteId(null);
      setPage('dashboard');
    }
  };

  const openSite = (site) => {
    setSelectedSiteId(site.id);
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
    setSelectedSiteId(null);
    setPage('dashboard');
  };

  const navChange = (newPage) => {
    setPage(newPage);
    setSelectedSiteId(null);
    setSelectedIssue(null);
  };

  const signOut = async () => {
    await api.logout();
    setUser(null);
    setSites([]);
    setSelectedSiteId(null);
    setSelectedIssue(null);
    setPage('dashboard');
    setView('landing');
  };

  const recheckSite = async () => {
    if (!selectedSite) return;
    await api.createAudit(selectedSite.rawUrl || `https://${selectedSite.url}`);
    await reloadSites();
  };

  const sidebarActive =
    page === 'audit' || page === 'issue'
      ? 'audits'
      : page;

  return (
    <UserContext.Provider value={user}>
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
          user={user}
          onUserUpdated={setUser}
          t={t}
        />
      )}
    </div>
    </UserContext.Provider>
  );
}
