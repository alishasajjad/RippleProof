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
      'Unable to create your account.'
    );
  } catch {
    return (
      'Unable to create your account. ' +
      'Please try again.'
    );
  }
}


function WorkspaceIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path
        d="M12 2.7 20 6v5.4c0 5.1-3.1 8.8-8 10.6-4.9-1.8-8-5.5-8-10.6V6l8-3.3Z"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />

      <path
        d="m8.7 12 2.1 2.1 4.6-4.6"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.9"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}


export default function RegisterPage() {
  const router =
    useRouter();


  const [
    name,
    setName,
  ] =
    useState('');


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
    confirmPassword,
    setConfirmPassword,
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
      !name.trim() ||
      !email.trim() ||
      !password ||
      !confirmPassword
    ) {
      setError(
        'Please complete all fields.',
      );

      return;
    }


    if (
      password.length < 8
    ) {
      setError(
        'Password must contain at least 8 characters.',
      );

      return;
    }


    if (
      password !==
      confirmPassword
    ) {
      setError(
        'Passwords do not match.',
      );

      return;
    }


    setLoading(true);


    try {
      const response =
        await fetch(
          '/api/auth/register',
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
                name:
                  name.trim(),

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
       * Registration endpoint
       * returns the auth session and
       * proxy stores JWT securely.
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
              'Unable to create your ' +
              'account. Please try again.'
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

                Evidence-first workspace
              </div>


              <h1
                className={
                  styles.heroTitle
                }
              >
                Build trust into
                every policy
                change.
              </h1>


              <p
                className={
                  styles.heroText
                }
              >
                Your RippleProof
                workspace combines
                semantic impact
                analysis, human
                approval, persistent
                evidence and
                deterministic
                verification.
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
                    Workspace
                    capabilities
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

                    Ready
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
                      Change discovery
                    </span>

                    <strong>
                      Semantic
                    </strong>
                  </div>


                  <div
                    className={
                      styles.proofRow
                    }
                  >
                    <span>
                      Repairs
                    </span>

                    <strong>
                      Human reviewed
                    </strong>
                  </div>


                  <div
                    className={
                      styles.proofRow
                    }
                  >
                    <span>
                      Proof
                    </span>

                    <strong>
                      Executable
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
                <WorkspaceIcon />
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
                  Identity + team ready
                </span>
              </div>
            </div>


            <h2
              className={
                styles.title
              }
            >
              Create your account.
            </h2>


            <p
              className={
                styles.subtitle
              }
            >
              Your first secure
              workspace will be
              created automatically.
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
                  htmlFor="name"
                  className={
                    styles.label
                  }
                >
                  Full name
                </label>


                <input
                  id="name"
                  name="name"
                  type="text"
                  autoComplete="name"
                  required
                  className={
                    styles.input
                  }
                  placeholder="Alisha Sajjad"
                  value={
                    name
                  }
                  onChange={
                    (
                      event,
                    ) => {
                      setName(
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
                  htmlFor="email"
                  className={
                    styles.label
                  }
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
                  htmlFor="password"
                  className={
                    styles.label
                  }
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
                    autoComplete="new-password"
                    required
                    minLength={8}
                    className={
                      styles.input
                    }
                    placeholder="At least 8 characters"
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


              <div
                className={
                  styles.field
                }
              >
                <label
                  htmlFor="confirmPassword"
                  className={
                    styles.label
                  }
                >
                  Confirm password
                </label>


                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={
                    showPassword
                      ? 'text'
                      : 'password'
                  }
                  autoComplete="new-password"
                  required
                  className={
                    styles.input
                  }
                  placeholder="Repeat your password"
                  value={
                    confirmPassword
                  }
                  onChange={
                    (
                      event,
                    ) => {
                      setConfirmPassword(
                        event.target
                          .value,
                      );
                    }
                  }
                />
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
                  ? 'Creating workspace...'
                  : (
                    <>
                      Create RippleProof
                      workspace

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
              Already have an
              account?{' '}

              <Link
                href="/login"
              >
                Sign in
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

                Secure identity
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

                Team workspace
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

                Audit ready
              </span>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}