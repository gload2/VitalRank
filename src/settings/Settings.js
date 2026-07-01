import { useState, useEffect } from 'react';
import { C } from '../common/colors';
import { TopBar } from '../common/components';
import { getPlans, updatePlan, updateProfile } from '../common/api';
import { getTheme, setTheme } from '../common/theme';
import './Settings.css';

export default function SettingsPage({ lang, onLangChange, user, onUserUpdated, t }) {
  const [name, setName] = useState(user?.name || '');
  const [nameSaved, setNameSaved] = useState(false);
  const [plans, setPlans] = useState([]);
  const [featureLabels, setFeatureLabels] = useState({});
  const [switching, setSwitching] = useState(null);
  const [theme, setThemeState] = useState(getTheme());

  useEffect(() => { setName(user?.name || ''); }, [user]);

  const handleTheme = (tm) => {
    setTheme(tm);
    setThemeState(tm);
  };

  useEffect(() => {
    let active = true;
    getPlans()
      .then((data) => {
        if (!active) return;
        setPlans(data.plans || []);
        setFeatureLabels(data.feature_labels || {});
      })
      .catch(() => {});
    return () => { active = false; };
  }, []);

  const email = user?.email || '';
  const currentPlan = user?.plan || 'free';
  const initial = (user?.name || email || 'U').charAt(0).toUpperCase();

  const handleSaveName = async () => {
    try {
      const updated = await updateProfile(name.trim() || null);
      onUserUpdated?.(updated);
      setNameSaved(true);
      setTimeout(() => setNameSaved(false), 2000);
    } catch { /* тихо игнорируем — форма останется как есть */ }
  };

  const handlePickPlan = async (planId) => {
    if (planId === currentPlan) return;
    setSwitching(planId);
    try {
      const updated = await updatePlan(planId);
      onUserUpdated?.(updated);
    } catch { /* ignore */ } finally {
      setSwitching(null);
    }
  };

  return (
    <div className="settings">
      <TopBar><span style={{ color: C.muted, fontSize: 18 }}>⚙</span></TopBar>

      <div className="settings__content">
        <h1 className="settings__title">{t('settings_title')}</h1>
        <p className="settings__sub">{t('settings_sub')}</p>

        {/* Profile */}
        <div className="settings__card">
          <div className="settings__card-head">
            <div className="settings__card-title">{t('settings_profile_title')}</div>
            <div className="settings__card-sub">{t('settings_profile_sub')}</div>
          </div>
          <div className="settings__account-row" style={{ marginBottom: 18 }}>
            <div className="settings__avatar">{initial}</div>
            <div>
              <div className="settings__account-name">{user?.name || email || t('settings_account_user')}</div>
              <div className="settings__account-plan">{email}</div>
            </div>
          </div>
          <label className="settings__field-label">{t('settings_name_label')}</label>
          <div className="settings__name-row">
            <input
              className="settings__input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={t('settings_name_ph')}
              maxLength={60}
            />
            <button className="settings__save-btn settings__save-btn--sm" onClick={handleSaveName}>
              {nameSaved ? t('settings_saved') : t('settings_name_save')}
            </button>
          </div>
        </div>

        {/* Plan */}
        <div className="settings__card">
          <div className="settings__card-head">
            <div className="settings__card-title">{t('settings_plan_title')}</div>
            <div className="settings__card-sub">{t('settings_plan_sub')}</div>
          </div>
          <div className="settings__plans">
            {plans.map((p) => {
              const isCurrent = p.id === currentPlan;
              const enabled = Object.keys(p.features || {}).filter((f) => p.features[f]);
              return (
                <div
                  key={p.id}
                  className={`settings__plan${isCurrent ? ' settings__plan--current' : ''}`}
                >
                  <div className="settings__plan-name">{p.label}</div>
                  <div className="settings__plan-price">{p.price}</div>
                  <div className="settings__plan-tagline">{p.tagline}</div>
                  <ul className="settings__plan-features">
                    <li>✓ {p.max_sites >= 1000 ? '∞' : p.max_sites} {t('settings_plan_sites')}</li>
                    {enabled.map((f) => (
                      <li key={f}>✓ {featureLabels[f] || f}</li>
                    ))}
                  </ul>
                  <button
                    className={`settings__plan-btn${isCurrent ? ' settings__plan-btn--current' : ''}`}
                    onClick={() => handlePickPlan(p.id)}
                    disabled={isCurrent || switching === p.id}
                  >
                    {isCurrent ? t('settings_plan_current')
                      : switching === p.id ? '...'
                      : t('settings_plan_choose')}
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* Language */}
        <div className="settings__card">
          <div className="settings__card-head">
            <div className="settings__card-title">{t('settings_lang_title')}</div>
            <div className="settings__card-sub">{t('settings_lang_sub')}</div>
          </div>
          <div className="settings__lang-options">
            <button
              className={`settings__lang-btn${lang === 'ru' ? ' settings__lang-btn--active' : ''}`}
              onClick={() => onLangChange('ru')}
            >
              🇷🇺 {t('settings_lang_ru')}
            </button>
            <button
              className={`settings__lang-btn${lang === 'en' ? ' settings__lang-btn--active' : ''}`}
              onClick={() => onLangChange('en')}
            >
              🇬🇧 {t('settings_lang_en')}
            </button>
          </div>
        </div>

        {/* Theme */}
        <div className="settings__card">
          <div className="settings__card-head">
            <div className="settings__card-title">{t('settings_theme_title')}</div>
            <div className="settings__card-sub">{t('settings_theme_sub')}</div>
          </div>
          <div className="settings__lang-options">
            <button
              className={`settings__lang-btn${theme === 'dark' ? ' settings__lang-btn--active' : ''}`}
              onClick={() => handleTheme('dark')}
            >
              🌑 {t('settings_theme_dark')}
            </button>
            <button
              className={`settings__lang-btn${theme === 'light' ? ' settings__lang-btn--active' : ''}`}
              onClick={() => handleTheme('light')}
            >
              ☀️ {t('settings_theme_light')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
