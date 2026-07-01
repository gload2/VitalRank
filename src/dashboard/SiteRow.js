import { useState } from 'react';
import { C } from '../common/colors';
import { ScoreRing, Pill } from '../common/components';
import './SiteRow.css';

export default function SiteRow({ site, badge, gc, yc, onOpen, onRemove, t }) {
  const [hover,      setHover]      = useState(false);
  const [confirmDel, setConfirmDel] = useState(false);

  return (
    <div
      className={`site-row${hover ? ' site-row--hover' : ''}`}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => { setHover(false); setConfirmDel(false); }}
      onClick={onOpen}
    >
      <ScoreRing score={site.health} />

      <div className="site-row__info">
        <div className="site-row__url">{site.url}</div>
        <div className="site-row__date">
          ↗ {t('dash_added')} {new Date(site.addedAt).toLocaleDateString(t('locale'))}
        </div>
      </div>

      <div className="site-row__scores">
        <div className="site-row__score">
          <div className="site-row__score-label">GOOGLE</div>
          <div className="site-row__score-val" style={{ color: site.google == null ? C.dim : gc }}>
            {site.google == null ? '—' : site.google}
          </div>
        </div>
        <div className="site-row__score">
          <div className="site-row__score-label">YANDEX</div>
          <div className="site-row__score-val" style={{ color: site.yandex == null ? C.dim : yc }}>
            {site.yandex == null ? '—' : site.yandex}
          </div>
        </div>
      </div>

      <Pill label={badge.label} color={badge.color} />

      <button
        className="site-row__btn-open"
        onClick={e => { e.stopPropagation(); onOpen(); }}
      >
        {t('dash_open')}
      </button>

      {confirmDel ? (
        <button
          className="site-row__btn-delete site-row__btn-delete--confirm"
          onClick={e => { e.stopPropagation(); onRemove(); }}
        >
          {t('dash_delete')}
        </button>
      ) : (
        <button
          className="site-row__btn-delete"
          onClick={e => { e.stopPropagation(); setConfirmDel(true); }}
        >
          ✕
        </button>
      )}
    </div>
  );
}
