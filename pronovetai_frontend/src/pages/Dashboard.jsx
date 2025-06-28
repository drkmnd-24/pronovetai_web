// ─── src/pages/Dashboard.jsx ─────────────────────────────────────────
import { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  /* ------------------------------------------------------------------ */
  /*  Simple helpers to call global ApexCharts once the component mounts */
  /* ------------------------------------------------------------------ */

  const profileChartRef = useRef(null);
  const europeRef       = useRef(null);
  const americaRef      = useRef(null);
  const indoRef         = useRef(null);

  useEffect(() => {
    /* Guard: if for some reason the global isn’t there. */
    if (!window.ApexCharts) return;

    // ① Profile-visit area chart  (very trimmed-down example)
    const profileOptions = {
      chart: { type: 'area', height: 200, toolbar: { show: false } },
      series: [{ name: 'Visits', data: [31, 40, 28, 51, 42, 109, 100] }],
      xaxis: { categories: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
      colors: ['#435ebe'],
    };
    const profileChart = new window.ApexCharts(profileChartRef.current, profileOptions);
    profileChart.render();

    // ② Tiny sparkline pies for region stats
    const pie = (el, val, color) =>
      new window.ApexCharts(el, {
        chart: { type: 'radialBar', height: 100, sparkline: { enabled: true } },
        series: [val],
        colors: [color],
        plotOptions: { radialBar: { hollow: { size: '60%' }, dataLabels: { show: false } } },
      }).render();

    pie(europeRef.current, 62, '#435ebe');
    pie(americaRef.current, 23, '#55c6e8');
    pie(indoRef.current, 75, '#ff7976');

    return () => {
      profileChart.destroy();
      // radial charts are auto-destroyed when their elements disappear
    };
  }, []);

  /* ------------------------------------------------------------------ */
  /*  Layout – a sliced-down version of the static HTML you pasted       */
  /* ------------------------------------------------------------------ */
  return (
    <div id="app">
      {/* ░░░░░░░░  SIDEBAR  ░░░░░░░░ */}
      <aside id="sidebar" className="sidebar-wrapper active">
        {/* -- logo + dark-mode toggle (kept from template) -- */}
        <div className="sidebar-header position-relative">
          <div className="d-flex justify-content-between align-items-center">
            <div className="logo">
              <Link to="/">
                <img src="../../public/mazer/img/logo.svg" alt="Logo" style={{ height: 28 }} />
              </Link>
            </div>
            {/* theme toggle switch left as-is; handled by initTheme.js */}
          </div>
        </div>

        {/* -- one or two menu items just to show the idea -- */}
        <ul className="menu">
          <li className="sidebar-title">Menu</li>
          <li className="sidebar-item active">
            <Link className="sidebar-link" to="/dashboard">
              <i className="bi bi-grid-fill" /> <span>Dashboard</span>
            </Link>
          </li>
          {/* …add more links as needed */}
        </ul>
      </aside>

      {/* ░░░░░░░░  MAIN  ░░░░░░░░ */}
      <div id="main" className="layout-navbar">
        <header className="mb-3">
          <a href="#!" className="burger-btn d-block d-xl-none">
            <i className="bi bi-justify fs-3" />
          </a>
        </header>

        {/* ---------- heading ---------- */}
        <div className="page-heading">
          <h3>Profile Statistics</h3>
        </div>

        {/* ---------- content ---------- */}
        <div className="page-content">
          <section className="row">
            {/* --- Stat cards (4x) --- */}
            {[
              { color: 'purple', icon: 'Show',  label: 'Profile Views', value: '112 000' },
              { color: 'blue',   icon: 'Profile', label: 'Followers',     value: '183 000' },
              { color: 'green',  icon: 'Add-User', label: 'Following',     value: '80 000' },
              { color: 'red',    icon: 'Bookmark', label: 'Saved Post',    value: '112' },
            ].map((c, i) => (
              <div key={i} className="col-6 col-lg-3 col-md-6">
                <div className="card">
                  <div className="card-body px-4 py-4-5">
                    <div className="row align-items-center">
                      <div className="col-4 d-flex justify-content-start">
                        <div className={`stats-icon ${c.color}`}>
                          <i className={`iconly-bold${c.icon}`} />
                        </div>
                      </div>
                      <div className="col-8 text-end">
                        <h6 className="text-muted font-semibold">{c.label}</h6>
                        <h6 className="font-extrabold mb-0">{c.value}</h6>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {/* --- Profile visit chart --- */}
            <div className="col-12">
              <div className="card">
                <div className="card-header"><h4>Profile Visit</h4></div>
                <div className="card-body">
                  <div ref={profileChartRef} /> {/* chart rendered by useEffect */}
                </div>
              </div>
            </div>

            {/* 2-column area (left = region pies, right = latest comments)… */}
            <div className="col-12 col-xl-4">
              <div className="card">
                <div className="card-header"><h4>Visitors by Region</h4></div>
                <div className="card-body">
                  {/* Europe */}
                  <div className="d-flex justify-content-between align-items-center mb-3">
                    <div className="d-flex align-items-center">
                      <svg className="bi text-primary" width="10" height="10">
                        <use xlinkHref="../../public/mazer/img/bootstrap-icons.svg#circle-fill" />
                      </svg>
                      <h6 className="mb-0 ms-2">Europe</h6>
                    </div>
                    <h6 className="mb-0">862</h6>
                  </div>
                  <div ref={europeRef} />

                  {/* America */}
                  <div className="d-flex justify-content-between align-items-center mt-4 mb-3">
                    <div className="d-flex align-items-center">
                      <svg className="bi text-success" width="10" height="10">
                        <use xlinkHref="../../public/mazer/img/bootstrap-icons.svg#circle-fill" />
                      </svg>
                      <h6 className="mb-0 ms-2">America</h6>
                    </div>
                    <h6 className="mb-0">375</h6>
                  </div>
                  <div ref={americaRef} />

                  {/* Indonesia */}
                  <div className="d-flex justify-content-between align-items-center mt-4 mb-3">
                    <div className="d-flex align-items-center">
                      <svg className="bi text-danger" width="10" height="10">
                        <use xlinkHref="../../public/mazer/img/bootstrap-icons.svg#circle-fill" />
                      </svg>
                      <h6 className="mb-0 ms-2">Indonesia</h6>
                    </div>
                    <h6 className="mb-0">1 025</h6>
                  </div>
                  <div ref={indoRef} />
                </div>
              </div>
            </div>

            {/* Right column – latest comments (static) */}
            <div className="col-12 col-xl-8">
              <div className="card">
                <div className="card-header"><h4>Latest Comments</h4></div>
                <div className="card-body table-responsive">
                  <table className="table table-hover">
                    <thead>
                      <tr><th>Name</th><th>Comment</th></tr>
                    </thead>
                    <tbody>
                      {[
                        { img: '../../public/mazer/img/5.jpg', name: 'Si Cantik', txt: 'Congratulations on your graduation!' },
                        { img: '../../public/mazer/img2.jpg', name: 'Si Ganteng', txt: 'Wow amazing design!' },
                      ].map((c, i) => (
                        <tr key={i}>
                          <td>
                            <div className="d-flex align-items-center">
                              <div className="avatar avatar-md">
                                <img src={`../../public/mazer/img/${c.img}`} alt="" />
                              </div>
                              <p className="font-bold ms-3 mb-0">{c.name}</p>
                            </div>
                          </td>
                          <td>{c.txt}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </section>
        </div>

        {/* Footer kept intact */}
        <footer className="mt-4">
          <div className="footer clearfix mb-0 text-muted">
            <div className="float-start">2023 © Mazer</div>
            <div className="float-end">
              Crafted with <span className="text-danger"><i className="bi bi-heart-fill" /></span> by&nbsp;
              <a href="https://saugi.me" target="_blank" rel="noreferrer">Saugi</a>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
