import { useState } from 'react';
import { C } from '../common/colors';
import { TopBar } from '../common/components';
import './Settings.css';

export default function SettingsPage({ lang, onLangChange, t }) {
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="settings">
      <TopBar><span style={{ color: C.muted, fontSize: 18 }}>⚙</span></TopBar>

      <div className="settings__content">
        <h1 className="settings__title">{t('settings_title')}</h1>
        <p className="settings__sub">{t('settings_sub')}</p>

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

        {/* Theme (placeholder) */}
        <div className="settings__card">
          <div className="settings__card-head">
            <div className="settings__card-title">{t('settings_theme_title')}</div>
            <div className="settings__card-sub">{t('settings_theme_sub')}</div>
          </div>
          <div className="settings__theme-preview">
            <div className="settings__theme-swatch settings__theme-swatch--active">
              🌑 {t('settings_theme_dark')}
            </div>
          </div>
        </div>

        {/* Account */}
        <div className="settings__card">
          <div className="settings__card-head">
            <div className="settings__card-title">{t('settings_account_title')}</div>
            <div className="settings__card-sub">{t('settings_account_sub')}</div>
          </div>
          <div className="settings__account-row">
            <div className="settings__avatar">U</div>
            <div>
              <div className="settings__account-name">{t('settings_account_user')}</div>
              <div className="settings__account-plan">{t('settings_account_plan')}</div>
            </div>
          </div>
        </div>

        <button className="settings__save-btn" onClick={handleSave}>
          {saved ? t('settings_saved') : t('settings_save')}
        </button>
      </div>
    </div>
  );
}
