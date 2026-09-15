'use client';

import Link from 'next/link';

import {
  useRouter,
} from 'next/navigation';

import {
  FormEvent,
  useState,
} from 'react';

import styles from '../auth.module.css';


type ApiErrorBody = {
  detail?: string;

  message?: string;

  error?: {
    code?: string;
    message?: string;
    request_id?: string;
  };
};


async function getErrorMessage(
  response: Response,
): Promise<string> {
  try {
    const body: ApiErrorBody =
      await response.json();

    return (
      body.error?.message ??
      body.detail ??
      body.message ??
      'Unable to sign in.'
    );
  } catch {
    return (
      'Unable to sign in. ' +
      'Please try again.'
    );
  }
}


function LockIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path
        d="M7 10V7a5 5 0 0 1 10 0v3"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />

      <rect
        x="5"
        y="10"
        width="14"
        height="11"
        rx="2"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
      />

      <path
        d="M12 14v3"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}


export default function LoginPage() {
  const router =
    useRouter();


  const [
    email,
    setEmail,
  ] =
    useState('');


  const [
    password,
    setPassword,
  ] =
    useState('');


  const [
    showPassword,
    setShowPassword,
  ] =
    useState(false);


  const [
    loading,
    setLoading,
  ] =
    useState(false);


  const [
    error,
    setError,
  ] =
    useState('');


  async function handleSubmit(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setError('');


    if (
      !email.trim() ||
      !password
    ) {
      setError(
        'Email and password are required.',
      );

      return;
    }


    setLoading(true);


    try {
      const response =
        await fetch(
          '/api/auth/login',
          {
            method:
              'POST',

            headers: {
              Accept:
                'application/json',

              'Content-Type':
                'application/json',
            },

            credentials:
              'include',

            cache:
              'no-store',

            body:
              JSON.stringify({
                email:
                  email
                    .trim()
                    .toLowerCase(),

                password,
              }),
          },
        );


      if (!response.ok) {
        const message =
          await getErrorMessage(
            response,
          );

        throw new Error(
          message,
        );
      }


      /*
       * Login proxy stores the JWT
       * inside an HTTP-only cookie.
       *
       * Do not store the JWT in
       * localStorage.
       */
      await response.json();


      router.replace(
        '/custom',
      );

      router.refresh();

    } catch (
      caughtError
    ) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : (
              'Unable to sign in. ' +
              'Please try again.'
            ),
      );

    } finally {
      setLoading(false);
    }
  }


  return (
    <main
      className={
        styles.page
      }
    >
      <div
        className={
          styles.container
        }
      >
        <div
          className={
            styles.shell
          }
        >
          <section
            className={
              styles.contextPanel
            }
          >
            <div
              className={
                styles.contextInner
              }
            >
              <div
                className={
                  styles.eyebrow
                }
              >
                <span
                  className={
                    styles.eyebrowDot
                  }
                />

                Secure workspace
              </div>


              <h1
                className={
                  styles.heroTitle
                }
              >
                Change one rule.

                <br />

                <span>
                  Prove everything
                  changed.
                </span>
              </h1>


              <p
                className={
                  styles.heroText
                }
              >
                Sign in to trace
                policy changes,
                review semantic
                dependencies,
                approve evidence-backed
                repairs and verify
                executable behaviour.
              </p>


              <div
                className={
                  styles.proofCard
                }
              >
                <div
                  className={
                    styles.proofHeader
                  }
                >
                  <strong>
                    RippleProof control
                    plane
                  </strong>


                  <span
                    className={
                      styles.operational
                    }
                  >
                    <span
                      className={
                        styles.operationalDot
                      }
                    />

                    Operational
                  </span>
                </div>


                <div
                  className={
                    styles.proofRows
                  }
                >
                  <div
                    className={
                      styles.proofRow
                    }
                  >
                    <span>
                      Semantic analysis
                    </span>

                    <strong>
                      Groq
                    </strong>
                  </div>


                  <div
                    className={
                      styles.proofRow
                    }
                  >
                    <span>
                      Audit persistence
                    </span>

                    <strong>
                      PostgreSQL
                    </strong>
                  </div>


                  <div
                    className={
                      styles.proofRow
                    }
                  >
                    <span>
                      Verification
                    </span>

                    <strong>
                      Deterministic
                    </strong>
                  </div>
                </div>
              </div>
            </div>
          </section>


          <section
            className={
              styles.formPanel
            }
          >
            <div
              className={
                styles.formBadge
              }
            >
              <div
                className={
                  styles.badgeIcon
                }
              >
                <LockIcon />
              </div>


              <div
                className={
                  styles.formBadgeText
                }
              >
                <strong>
                  RippleProof workspace
                </strong>

                <span>
                  Protected access
                </span>
              </div>
            </div>


            <h2
              className={
                styles.title
              }
            >
              Welcome back.
            </h2>


            <p
              className={
                styles.subtitle
              }
            >
              Sign in to analyze
              policy changes, review
              evidence and verify
              execution.
            </p>


            <form
              className={
                styles.form
              }
              onSubmit={
                handleSubmit
              }
            >
              {error && (
                <div
                  className={
                    styles.error
                  }
                  role="alert"
                >
                  {error}
                </div>
              )}


              <div
                className={
                  styles.field
                }
              >
                <label
                  className={
                    styles.label
                  }
                  htmlFor="email"
                >
                  Email address
                </label>


                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  className={
                    styles.input
                  }
                  placeholder="you@company.com"
                  value={
                    email
                  }
                  onChange={
                    (
                      event,
                    ) => {
                      setEmail(
                        event.target
                          .value,
                      );
                    }
                  }
                />
              </div>


              <div
                className={
                  styles.field
                }
              >
                <label
                  className={
                    styles.label
                  }
                  htmlFor="password"
                >
                  Password
                </label>


                <div
                  className={
                    styles.passwordWrap
                  }
                >
                  <input
                    id="password"
                    name="password"
                    type={
                      showPassword
                        ? 'text'
                        : 'password'
                    }
                    autoComplete="current-password"
                    required
                    className={
                      styles.input
                    }
                    placeholder="Your password"
                    value={
                      password
                    }
                    onChange={
                      (
                        event,
                      ) => {
                        setPassword(
                          event.target
                            .value,
                        );
                      }
                    }
                  />


                  <button
                    type="button"
                    className={
                      styles.passwordToggle
                    }
                    onClick={() => {
                      setShowPassword(
                        (
                          current,
                        ) =>
                          !current,
                      );
                    }}
                  >
                    {showPassword
                      ? 'Hide'
                      : 'Show'}
                  </button>
                </div>
              </div>


              <button
                type="submit"
                disabled={
                  loading
                }
                className={
                  styles.submit
                }
              >
                {loading && (
                  <span
                    className={
                      styles.spinner
                    }
                  />
                )}


                {loading
                  ? 'Signing in...'
                  : (
                    <>
                      Sign in to
                      RippleProof

                      <span>
                        →
                      </span>
                    </>
                  )}
              </button>
            </form>


            <p
              className={
                styles.footerText
              }
            >
              New to RippleProof?{' '}

              <Link
                href="/register"
              >
                Create an account
              </Link>
            </p>


            <div
              className={
                styles.securityStrip
              }
            >
              <span
                className={
                  styles.securityItem
                }
              >
                <span
                  className={
                    styles.securityCheck
                  }
                >
                  ✓
                </span>

                Secure session
              </span>


              <span
                className={
                  styles.securityItem
                }
              >
                <span
                  className={
                    styles.securityCheck
                  }
                >
                  ✓
                </span>

                Audit trail
              </span>


              <span
                className={
                  styles.securityItem
                }
              >
                <span
                  className={
                    styles.securityCheck
                  }
                >
                  ✓
                </span>

                Human approval
              </span>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}