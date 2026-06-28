import { useState, useRef } from 'react';
import { C } from '../common/colors';
import './AddSiteModal.css';

export default function AddSiteModal({ onClose, onAdd, t }) {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const inputRef = useRef(null);

  const clean = (raw) =>
    raw.trim().replace(/^https?:\/\//, '').replace(/\/$/, '');

  const handleSubmit = () => {
    const cleaned = clean(url);

    if (!cleaned) {
      setError(t('modal_err_empty'));
      return;
    }

    if (!/^[\w.-]+\.\w{2,}/.test(cleaned)) {
      setError(t('modal_err_invalid'));
      return;
    }

    setError('');

    // Сайт добавляется в статусе "ожидает анализа".
    // Оценки и список проблем заполнит backend/ML после подключения.
    onAdd({
      id: Date.now(),
      url: cleaned,
      addedAt: new Date().toISOString(),
      status: 'pending',
      health: null,
      google: null,
      yandex: null,
      googleIssues: [],
      yandexIssues: [],
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal__header">
          <h2 className="modal__title">{t('modal_title')}</h2>
          <button className="modal__close" onClick={onClose}>
            ×
          </button>
        </div>

        <label className="modal__label">
          {t('modal_label')}
        </label>

        <input
          ref={inputRef}
          autoFocus
          value={url}
          onChange={(e) => {
            setUrl(e.target.value);
            setError('');
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              handleSubmit();
            }
          }}
          placeholder={t('modal_placeholder')}
          className={`modal__input${error ? ' modal__input--error' : ''}`}
        />

        {error && (
          <div className="modal__error">
            {error}
          </div>
        )}

        <div className="modal__actions">
          <button
            className="modal__btn-cancel"
            onClick={onClose}
          >
            {t('modal_cancel')}
          </button>

          <button
            className="modal__btn-submit"
            onClick={handleSubmit}
            disabled={!url.trim()}
            style={{ background: C.blue }}
          >
            {t('modal_submit')}
          </button>
        </div>
      </div>
    </div>
  );
}