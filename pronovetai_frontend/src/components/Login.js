// src/components/Login.js
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import API from '../api';

export default function Login() {
  const navigate = useNavigate();

  const [form, setForm]   = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [keepLoggedIn, setKeepLoggedIn] = useState(false);   // for the checkbox

  /* -------------------------------------------------- handlers */

  const handleChange = (e) =>
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const { data } = await API.post('token/', form);

      // Tokens + “remember me” logic
      localStorage.setItem('accessToken',  data.access);
      localStorage.setItem('refreshToken', data.refresh);
      localStorage.setItem('username',     form.username);
      if (keepLoggedIn) localStorage.setItem('keepLoggedIn', '1');

      navigate('/dashboard');
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.non_field_errors?.[0] ||
        'Invalid credentials, please try again.';
      setError(msg);
    }
  };

  /* -------------------------------------------------- render */

  return (
    <div className="relative flex flex-col min-h-screen bg-white dark:bg-gray-900 lg:flex-row">
      {/* ---------- Left column – form ---------- */}
      <div className="flex flex-col flex-1 w-full lg:w-1/2">
        <div className="w-full max-w-md pt-10 mx-auto">
          <Link
            to="/"
            className="inline-flex items-center text-sm text-gray-500 transition-colors hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
          >
            <svg
              className="stroke-current"
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 20 20"
              fill="none"
            >
              <path
                d="M12.7083 5L7.5 10.2083L12.7083 15.4167"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            Back to dashboard
          </Link>
        </div>

        <div className="flex flex-col justify-center flex-1 w-full max-w-md mx-auto">
          {/* ------ heading ------ */}
          <div className="mb-5 sm:mb-8">
            <h1 className="mb-2 font-semibold text-gray-800 text-title-sm dark:text-white/90 sm:text-title-md">
              Sign In
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Enter your username and password to sign in!
            </p>
          </div>

          {/* ------ 3rd-party buttons (non-functional placeholders) ------ */}
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-5">
            <button
              type="button"
              className="inline-flex items-center justify-center gap-3 px-7 py-3 text-sm font-normal text-gray-700 transition-colors bg-gray-100 rounded-lg hover:bg-gray-200 hover:text-gray-800 dark:bg-white/5 dark:text-white/90 dark:hover:bg-white/10"
            >
              {/* Google icon */}
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                {/* paths omitted for brevity */}
              </svg>
              Sign in with Google
            </button>

            <button
              type="button"
              className="inline-flex items-center justify-center gap-3 px-7 py-3 text-sm font-normal text-gray-700 transition-colors bg-gray-100 rounded-lg hover:bg-gray-200 hover:text-gray-800 dark:bg-white/5 dark:text-white/90 dark:hover:bg-white/10"
            >
              {/* X / Twitter icon */}
              <svg
                width="20"
                height="20"
                viewBox="0 0 21 20"
                fill="currentColor"
                xmlns="http://www.w3.org/2000/svg"
              >
                {/* path omitted */}
              </svg>
              Sign in with X
            </button>
          </div>

          {/* divider */}
          <div className="relative py-5">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200 dark:border-gray-800" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-5 py-2 text-gray-400 bg-white dark:bg-gray-900">
                Or
              </span>
            </div>
          </div>

          {/* ------ form ------ */}
          {error && (
            <p className="mb-4 text-sm text-center text-error-500">{error}</p>
          )}

          <form onSubmit={handleSubmit}>
            <div className="space-y-5">
              {/* username / email */}
              <div>
                <label
                  htmlFor="username"
                  className="block mb-1.5 text-sm font-medium text-gray-700 dark:text-gray-400"
                >
                  Username<span className="text-error-500">*</span>
                </label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  placeholder="your.username"
                  value={form.username}
                  onChange={handleChange}
                  required
                  className="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
                />
              </div>

              {/* password + toggle */}
              <div>
                <label
                  htmlFor="password"
                  className="block mb-1.5 text-sm font-medium text-gray-700 dark:text-gray-400"
                >
                  Password<span className="text-error-500">*</span>
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    name="password"
                    placeholder="Enter your password"
                    value={form.password}
                    onChange={handleChange}
                    required
                    className="h-11 w-full rounded-lg border border-gray-300 bg-transparent py-2.5 pl-4 pr-11 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
                  />
                  <span
                    onClick={() => setShowPassword((p) => !p)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 cursor-pointer text-gray-500 dark:text-gray-400"
                  >
                    {showPassword ? (
                      /* eye-off icon */
                      <svg
                        className="fill-current"
                        width="20"
                        height="20"
                        viewBox="0 0 20 20"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        {/* path omitted */}
                      </svg>
                    ) : (
                      /* eye icon */
                      <svg
                        className="fill-current"
                        width="20"
                        height="20"
                        viewBox="0 0 20 20"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        {/* path omitted */}
                      </svg>
                    )}
                  </span>
                </div>
              </div>

              {/* remember me + forgot */}
              <div className="flex items-center justify-between">
                <label
                  htmlFor="keepLogged"
                  className="flex items-center text-sm font-normal text-gray-700 cursor-pointer select-none dark:text-gray-400"
                >
                  <input
                    id="keepLogged"
                    type="checkbox"
                    className="sr-only"
                    checked={keepLoggedIn}
                    onChange={() => setKeepLoggedIn((v) => !v)}
                  />
                  <span
                    className={`mr-3 flex h-5 w-5 items-center justify-center rounded-md border-[1.25px] ${
                      keepLoggedIn
                        ? 'border-brand-500 bg-brand-500'
                        : 'border-gray-300 dark:border-gray-700'
                    }`}
                  >
                    {keepLoggedIn && (
                      <svg
                        width="14"
                        height="14"
                        viewBox="0 0 14 14"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path
                          d="M11.6667 3.5L5.25 9.91667L2.33337 7"
                          stroke="white"
                          strokeWidth="1.94437"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    )}
                  </span>
                  Keep me logged in
                </label>

                <Link
                  to="/reset-password"
                  className="text-sm text-brand-500 hover:text-brand-600 dark:text-brand-400"
                >
                  Forgot password?
                </Link>
              </div>

              {/* submit */}
              <button
                type="submit"
                className="flex items-center justify-center w-full px-4 py-3 text-sm font-medium text-white transition rounded-lg bg-brand-500 shadow-theme-xs hover:bg-brand-600"
              >
                Sign In
              </button>
            </div>
          </form>

          {/* sign-up link */}
          <p className="mt-5 text-sm font-normal text-center text-gray-700 dark:text-gray-400">
            Don&apos;t have an account?{' '}
            <Link
              to="/register/staff"
              className="text-brand-500 hover:text-brand-600 dark:text-brand-400"
            >
              Sign Up
            </Link>
          </p>
        </div>
      </div>

      {/* ---------- Right column – marketing panel ---------- */}
      <div className="relative items-center justify-center flex-1 hidden w-full h-full bg-brand-950 dark:bg-white/5 lg:grid lg:w-1/2">
        {/* You can drop in your own artwork here */}
        <div className="flex flex-col items-center max-w-xs text-center">
          <img
            src="/tailadmin-html/images/logo/auth-logo.svg"
            alt="Pronove TAI"
            className="mb-4"
          />
          <p className="text-gray-400 dark:text-white/60">
            Free and Open-Source Tailwind CSS Admin Dashboard Template
          </p>
        </div>
      </div>
    </div>
  );
}
