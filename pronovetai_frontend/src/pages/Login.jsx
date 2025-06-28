// ─── src/pages/Login.jsx ──────────────────────────────────────────────────────
import  { useState } from 'react';
import  { useNavigate, Link } from 'react-router-dom';
import  API from '../api';

export default function Login() {
  /* ───────────────────────────────────────── state */
  const navigate         = useNavigate();
  const [form,  setForm] = useState({ username: '', password: '' });
  const [showPw, setShowPw] = useState(false);
  const [keep,   setKeep]   = useState(false);
  const [error,  setError]  = useState('');

  /* ───────────────────────────────────────── handlers */
  const handle = e => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async e => {
    e.preventDefault();
    setError('');

    try {
      const { data } = await API.post('token/', form);

      localStorage.setItem('accessToken',  data.access);
      localStorage.setItem('refreshToken', data.refresh);
      localStorage.setItem('username',     form.username);
      if (keep) localStorage.setItem('keepLoggedIn', '1');

      navigate('/dashboard');
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.response?.data?.non_field_errors?.[0] ||
        'Invalid credentials, please try again.',
      );
    }
  };

  /* ───────────────────────────────────────── render */
  return (
    <div id="auth" className="min-vh-100 d-flex">
      <div className="row flex-grow-1 w-100 m-0">
        {/* ── Left column – form ────────────────────────────────────── */}
        <div className="col-lg-5 col-12 d-flex align-items-center">
          <div id="auth-left" className="w-100 px-4 px-sm-5">
            {/* logo */}
            <div className="auth-logo mb-4 text-center text-lg-start">
              <Link to="/">
                <img
                  src="../vendor/mazer/img/logo.svg"
                  alt="Logo"
                  style={{ height: 40 }}
                />
              </Link>
            </div>

            <h1 className="auth-title mb-1">Log in.</h1>
            <p className="auth-subtitle mb-4">
              Welcome to Pronove TAI
            </p>

            {/* errors */}
            {error && (
              <div className="alert alert-danger py-2">{error}</div>
            )}

            <form onSubmit={submit}>
              {/* username */}
              <div className="form-group position-relative has-icon-left mb-4">
                <input
                  type="text"
                  className="form-control form-control-xl"
                  placeholder="Username"
                  name="username"
                  value={form.username}
                  onChange={handle}
                  required
                />
                <div className="form-control-icon">
                  <i className="bi bi-person" />
                </div>
              </div>

              {/* password */}
              <div className="form-group position-relative has-icon-left mb-4">
                <input
                  type={showPw ? 'text' : 'password'}
                  className="form-control form-control-xl"
                  placeholder="Password"
                  name="password"
                  value={form.password}
                  onChange={handle}
                  required
                />
                <div className="form-control-icon">
                  <i className="bi bi-shield-lock" />
                </div>
              </div>

              {/* show / keep checkboxes */}
              <div className="d-flex justify-content-between align-items-center mb-2">
                <div className="form-check">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    id="showPw"
                    checked={showPw}
                    onChange={() => setShowPw(!showPw)}
                  />
                  <label className="form-check-label" htmlFor="showPw">
                    Show password
                  </label>
                </div>

                <div className="form-check form-check-lg d-flex align-items-end">
                  <input
                    className="form-check-input me-2"
                    type="checkbox"
                    id="keepMe"
                    checked={keep}
                    onChange={() => setKeep(!keep)}
                  />
                  <label className="form-check-label" htmlFor="keepMe">
                    Keep me logged in
                  </label>
                </div>
              </div>

              <button
                type="submit"
                className="btn btn-primary btn-block btn-lg shadow-lg mt-3 w-100"
              >
                Log in
              </button>
            </form>

            <div className="text-center mt-4 fs-6">
              <p className="text-gray-600">
                Don’t have an account?{' '}
                <Link to="/register/staff" className="font-bold">
                  Sign up
                </Link>
                .
              </p>
              <p>
                <Link to="/reset-password" className="font-bold">
                  Forgot password?
                </Link>
                .
              </p>
            </div>
          </div>
        </div>

        {/* ── Right column – hero / artwork ─────────────────────────── */}
        <div className="col-lg-7 d-none d-lg-block" id="auth-right">
          {/* empty on purpose – use as hero image / illustration area */}
        </div>
      </div>
    </div>
  );
}
