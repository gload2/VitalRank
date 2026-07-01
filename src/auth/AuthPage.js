import { useState } from 'react';
import * as api from '../common/api';
import { ApiError } from '../common/api';
import './AuthPage.css';

export default function AuthPage({ mode = 'login', onSuccess, onBack, t }) {
  const [tab, setTab] = useState(mode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const isRegister = tab === 'register';

  const validate = () => {
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      setError(t('auth_err_email'));
      return false;
    }
    if (password.length < 6) {
      setError(t('auth_err_password'));
      return false;
    }
    return true;
  };

  const submit = async () => {
    if (loading) return;
    setError('');
    if (!validate()) return;

    setLoading(true);
    try {
      if (isRegister) {
        await api.register(email.trim(), password);
      } else {
        await api.login(email.trim(), password);
      }
      const user = await api.me();
      onSuccess(user);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : t('auth_err_generic'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth">
      <div className="auth__card">
        <div className="auth__brand">VitalRank</div>
        <h1 className="auth__title">
          {isRegister ? t('auth_register_title') : t('auth_login_title')}
        </h1>

        <label className="auth__label">{t('auth_email')}</label>
        <input
          className="auth__input"
          type="email"
          autoFocus
          value={email}
          placeholder={t('auth_email_ph')}
          onChange={(e) => { setEmail(e.target.value); setError(''); }}
          onKeyDown={(e) => e.key === 'Enter' && submit()}
        />

        <label className="auth__label">{t('auth_password')}</label>
        <input
          className="auth__input"
          type="password"
          value={password}
          placeholder={t('auth_password_ph')}
          onChange={(e) => { setPassword(e.target.value); setError(''); }}
          onKeyDown={(e) => e.key === 'Enter' && submit()}
        />

        {error && <div className="auth__error">{error}</div>}

        <button className="auth__submit" onClick={submit} disabled={loading}>
          {loading
            ? t('auth_loading')
            : isRegister ? t('auth_register_btn') : t('auth_login_btn')}
        </button>

        <div
          className="auth__switch"
          onClick={() => { setTab(isRegister ? 'login' : 'register'); setError(''); }}
        >
          {isRegister ? t('auth_to_login') : t('auth_to_register')}
        </div>

        <div className="auth__back" onClick={onBack}>{t('auth_back')}</div>
      </div>
    </div>
  );
}
