import { useState } from 'react';
import './Landing.css';

export default function LandingPage({ onEnter, t }) {
  const [url, setUrl] = useState('');
  const [hovNav, setHovNav] = useState(null);

  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  const navLinks = [
    { key: 'nav_features',  target: 'features',  label: t('nav_features')  },
    { key: 'nav_pricing',   target: 'pricing',   label: t('nav_pricing')   },
    { key: 'nav_solutions', target: 'solutions', label: t('nav_solutions') },
  ];

  const features = [
    { icon: '⚡', title: t('feat_perf_title'), desc: t('feat_perf_desc') },
    { icon: '🛡', title: t('feat_sec_title'),  desc: t('feat_sec_desc')  },
    { icon: '🔍', title: t('feat_seo_title'),  desc: t('feat_seo_desc')  },
    { icon: '🤖', title: t('feat_ml_title'),   desc: t('feat_ml_desc')   },
  ];

  const plans = [
    {
      name: t('price_free_name'), amount: t('price_free_amount'), period: t('price_free_period'),
      features: [t('price_free_f1'), t('price_free_f2'), t('price_free_f3')], popular: false,
    },
    {
      name: t('price_pro_name'), amount: t('price_pro_amount'), period: t('price_pro_period'),
      features: [t('price_pro_f1'), t('price_pro_f2'), t('price_pro_f3')], popular: true,
    },
    {
      name: t('price_biz_name'), amount: t('price_biz_amount'), period: t('price_biz_period'),
      features: [t('price_biz_f1'), t('price_biz_f2'), t('price_biz_f3')], popular: false,
    },
  ];

  const solutions = [
    { icon: '🏢', title: t('sol_agency_title'), desc: t('sol_agency_desc') },
    { icon: '🛒', title: t('sol_ecom_title'),   desc: t('sol_ecom_desc')   },
    { icon: '⟨/⟩', title: t('sol_dev_title'),   desc: t('sol_dev_desc')    },
  ];

  return (
    <div className="landing">
      {/* ── Nav ── */}
      <nav className="landing__nav">
        <span className="landing__brand">VitalRank</span>

        <div className="landing__nav-links">
          {navLinks.map(({ key, target, label }) => (
            <span
              key={key}
              className={`landing__nav-link${hovNav === key ? ' landing__nav-link--hover' : ''}`}
              onMouseEnter={() => setHovNav(key)}
              onMouseLeave={() => setHovNav(null)}
              onClick={() => scrollTo(target)}
            >
              {label}
            </span>
          ))}
        </div>

        <div className="landing__nav-actions">
          <span className="landing__login" onClick={onEnter}>{t('nav_login')}</span>
          <button className="landing__get-started" onClick={onEnter}>
            {t('nav_get_started')}
          </button>
        </div>
      </nav>

      {/* ── Hero ── */}
      <div className="landing__hero">
        <div className="landing__badge">{t('landing_badge')}</div>

        <h1 className="landing__h1">
          {t('landing_h1a')}{' '}
          <span className="landing__h1-accent">{t('landing_h1b')}</span>
        </h1>

        <p className="landing__sub">{t('landing_sub')}</p>

        <div className="landing__cta-row">
          <input
            className="landing__input"
            value={url}
            onChange={e => setUrl(e.target.value)}
            placeholder={t('landing_input')}
            onKeyDown={e => e.key === 'Enter' && onEnter()}
          />
          <button className="landing__btn-primary" onClick={onEnter}>
            {t('landing_cta')}
          </button>
          <button className="landing__btn-ghost" onClick={onEnter}>
            {t('landing_demo')}
          </button>
        </div>
      </div>

      {/* ── Features ── */}
      <section id="features" className="landing__section">
        <h2 className="landing__section-title">{t('sec_features_title')}</h2>
        <p className="landing__section-sub">{t('sec_features_sub')}</p>
        <div className="landing__grid">
          {features.map(f => (
            <div key={f.title} className="landing__card">
              <div className="landing__card-icon">{f.icon}</div>
              <h3 className="landing__card-title">{f.title}</h3>
              <p className="landing__card-desc">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Pricing ── */}
      <section id="pricing" className="landing__section landing__section--alt">
        <h2 className="landing__section-title">{t('sec_pricing_title')}</h2>
        <p className="landing__section-sub">{t('sec_pricing_sub')}</p>
        <div className="landing__plans">
          {plans.map(plan => (
            <div
              key={plan.name}
              className={`landing__plan${plan.popular ? ' landing__plan--popular' : ''}`}
            >
              {plan.popular && <div className="landing__plan-badge">{t('price_popular')}</div>}
              <div className="landing__plan-name">{plan.name}</div>
              <div className="landing__plan-price">
                {plan.amount}<span className="landing__plan-period">{plan.period}</span>
              </div>
              <ul className="landing__plan-features">
                {plan.features.map(f => (
                  <li key={f} className="landing__plan-feature">✓ {f}</li>
                ))}
              </ul>
              <button
                className={`landing__plan-btn${plan.popular ? ' landing__plan-btn--primary' : ''}`}
                onClick={onEnter}
              >
                {t('price_cta')}
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* ── Solutions ── */}
      <section id="solutions" className="landing__section">
        <h2 className="landing__section-title">{t('sec_solutions_title')}</h2>
        <p className="landing__section-sub">{t('sec_solutions_sub')}</p>
        <div className="landing__grid">
          {solutions.map(s => (
            <div key={s.title} className="landing__card">
              <div className="landing__card-icon">{s.icon}</div>
              <h3 className="landing__card-title">{s.title}</h3>
              <p className="landing__card-desc">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="landing__footer">{t('audit_footer')}</footer>
    </div>
  );
}
