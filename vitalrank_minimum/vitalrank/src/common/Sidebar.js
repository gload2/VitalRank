import { C } from '../common/colors';
import './Sidebar.css';

export default function Sidebar({ active, onChange, onSignOut, t }) {
  const items = [
    { id: 'dashboard', icon: '⊞', label: t('sidebar_dashboard') },
    { id: 'audits',    icon: '◎', label: t('sidebar_audits')    },
    { id: 'problems',  icon: '↗', label: t('sidebar_problems')  },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar__logo">VitalRank</div>

      <nav className="sidebar__nav">
        {items.map(item => (
          <div
            key={item.id}
            onClick={() => onChange(item.id)}
            className={`sidebar__item${active === item.id ? ' sidebar__item--active' : ''}`}
          >
            <span className="sidebar__icon">{item.icon}</span>
            {item.label}
          </div>
        ))}
      </nav>

      <div className="sidebar__footer">
        <div
          className="sidebar__footer-item"
          onClick={() => onChange('settings')}
          style={{ color: active === 'settings' ? C.blue : C.muted }}
        >
          {t('sidebar_settings')}
        </div>
        <div
          className="sidebar__footer-item sidebar__footer-item--red"
          onClick={onSignOut}
        >
          {t('sidebar_signout')}
        </div>
      </div>
    </div>
  );
}
