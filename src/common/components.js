import { useState } from 'react';
import { C, scoreColor } from './colors';
import { useUser } from './UserContext';
import { translateIssue } from './i18n';
import './components.css';

export function ScoreRing({ score, size = 44 }) {
  const has   = typeof score === 'number';
  const col   = has ? scoreColor(score) : C.dim;
  const r     = size / 2 - 4;
  const circ  = 2 * Math.PI * r;
  const dash  = has ? (score / 100) * circ : 0;
  return (
    <div style={{ position: 'relative', width: size, height: size, flexShrink: 0 }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={C.border} strokeWidth={3} />
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={col}
          strokeWidth={3} strokeDasharray={`${dash} ${circ}`} strokeLinecap="round" />
      </svg>
      <span style={{
        position: 'absolute', inset: 0, display: 'flex', alignItems: 'center',
        justifyContent: 'center', color: col, fontWeight: 700,
        fontSize: size < 44 ? 12 : 14,
      }}>{has ? score : '—'}</span>
    </div>
  );
}

export function Pill({ label, color }) {
  return (
    <span style={{
      padding: '2px 10px', borderRadius: 20, fontSize: 11, fontWeight: 600,
      border: `1px solid ${color}44`, color, background: `${color}18`,
      whiteSpace: 'nowrap',
    }}>{label}</span>
  );
}

export function Spinner({ small }) {
  const size = small ? 14 : 18;
  return (
    <div style={{
      width: size, height: size,
      border: '2px solid #ffffff44',
      borderTop: `2px solid ${C.blue}`,
      borderRadius: '50%',
      animation: 'spin 0.8s linear infinite',
      flexShrink: 0,
    }} />
  );
}

export function IssueCard({ issue, onClick, t }) {
  const [hover, setHover] = useState(false);
  const { title, desc } = translateIssue(t, issue.ruleId, issue.title, issue.desc);
  const icon = issue.type === 'error'
    ? <span style={{ color: C.red,    fontSize: 16, flexShrink: 0 }}>⊘</span>
    : <span style={{ color: C.yellow, fontSize: 16, flexShrink: 0 }}>△</span>;
  return (
    <div
      onClick={() => onClick(issue)}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        background: C.surface, border: `1px solid ${hover ? C.blue : C.border}`,
        borderRadius: 10, padding: '12px 16px', cursor: 'pointer', marginBottom: 8,
        transition: 'border-color .15s',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12, overflow: 'hidden' }}>
        <div style={{ marginTop: 2 }}>{icon}</div>
        <div style={{ overflow: 'hidden' }}>
          <div style={{
            fontWeight: 600, fontSize: 14, color: C.text,
            whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
          }}>{title}</div>
          <div style={{
            fontSize: 12, color: C.muted, marginTop: 2,
            whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
          }}>{desc}</div>
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0, marginLeft: 12 }}>
        <Pill label={`${t('eff_short')}: ${issue.eff}`}    color={C.blueLight} />
        <Pill label={`${t('effort_short')}: ${issue.effort}`} color={C.dim} />
        <span style={{ color: C.dim, fontSize: 14 }}>→</span>
      </div>
    </div>
  );
}

const PLAN_LABELS = { free: 'Free', pro: 'Pro', business: 'Business' };

export function TopBar({ children }) {
  const user = useUser();
  const [open, setOpen] = useState(false);

  const displayName = user?.name || user?.email || 'User';
  const initial = (user?.name || user?.email || 'U').charAt(0).toUpperCase();
  const planLabel = PLAN_LABELS[user?.plan] || 'Free';

  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '14px 28px', borderBottom: `1px solid ${C.border}`,
      background: C.surface, position: 'sticky', top: 0, zIndex: 10,
    }}>
      <span style={{ color: C.blue, fontWeight: 800, fontSize: 18 }}>VitalRank</span>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        {children}
        <div style={{ position: 'relative' }}>
          <div
            onClick={() => setOpen((o) => !o)}
            title={displayName}
            style={{
              width: 32, height: 32, borderRadius: '50%', background: C.blue,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 13, fontWeight: 700, color: C.text, position: 'relative',
              cursor: 'pointer', userSelect: 'none',
            }}
          >
            {initial}
            <span style={{
              position: 'absolute', top: -2, right: -2, width: 10, height: 10,
              background: C.green, borderRadius: '50%', border: `2px solid ${C.surface}`,
            }} />
          </div>

          {open && (
            <>
              <div
                onClick={() => setOpen(false)}
                style={{ position: 'fixed', inset: 0, zIndex: 20 }}
              />
              <div style={{
                position: 'absolute', top: 42, right: 0, minWidth: 220, zIndex: 21,
                background: C.surface, border: `1px solid ${C.border}`, borderRadius: 10,
                padding: 14, boxShadow: '0 12px 30px rgba(0,0,0,0.5)',
              }}>
                <div style={{ color: C.text, fontWeight: 600, fontSize: 14, marginBottom: 2, wordBreak: 'break-word' }}>
                  {displayName}
                </div>
                {user?.email && (
                  <div style={{ color: C.muted, fontSize: 12, marginBottom: 10, wordBreak: 'break-word' }}>
                    {user.email}
                  </div>
                )}
                <span style={{
                  display: 'inline-block', padding: '3px 10px', borderRadius: 20, fontSize: 11,
                  fontWeight: 600, color: C.blueLight, background: `${C.blue}18`,
                  border: `1px solid ${C.blue}44`,
                }}>
                  {planLabel}
                </span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
