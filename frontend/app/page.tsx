import Link from 'next/link';

import {
  ArrowRight,
  BrainCircuit,
  CheckCircle2,
  Database,
  FileCheck2,
  FlaskConical,
  GitBranch,
  History,
  LockKeyhole,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  Workflow,
} from 'lucide-react';

import styles from './home.module.css';


const workflow = [
  {
    number: '01',
    title: 'Define the change',
    description:
      'Provide the previous and updated business policy.',
    icon: FileCheck2,
  },
  {
    number: '02',
    title: 'Trace the ripple',
    description:
      'AI discovers semantic dependencies across documents, prompts, forms and code.',
    icon: GitBranch,
  },
  {
    number: '03',
    title: 'Review repairs',
    description:
      'RippleProof proposes evidence-backed patches while a human remains in control.',
    icon: ShieldCheck,
  },
  {
    number: '04',
    title: 'Prove behaviour',
    description:
      'Deterministic boundary tests verify that the new rule is actually enforced.',
    icon: FlaskConical,
  },
];


const capabilities = [
  {
    title: 'Semantic impact analysis',
    description:
      'Find policy dependencies even when artifacts describe the same rule using different language.',
    icon: BrainCircuit,
  },
  {
    title: 'Executable proof',
    description:
      'Move beyond AI explanation with deterministic tests against machine-verifiable contracts.',
    icon: CheckCircle2,
  },
  {
    title: 'Human approval',
    description:
      'Every proposed repair stays reviewable before verification or operational acceptance.',
    icon: LockKeyhole,
  },
  {
    title: 'Persistent evidence',
    description:
      'Runs, findings, patches and verification results are persisted in PostgreSQL.',
    icon: Database,
  },
];


export default function HomePage() {
  return (
    <main
      className={
        styles.page
      }
    >


      <section
        className={
          styles.hero
        }
      >
        <div
          className={
            styles.heroGlowOne
          }
        />

        <div
          className={
            styles.heroGlowTwo
          }
        />


        <div
          className={
            styles.heroInner
          }
        >
          <div
            className={
              styles.heroCopy
            }
          >
            <div
              className={
                styles.eyebrow
              }
            >
              <Sparkles
                size={15}
              />

              SEMANTIC CHANGE INTELLIGENCE
              + EXECUTABLE PROOF
            </div>


            <h1>
              Change one rule.
              <span>
                Prove everything changed.
              </span>
            </h1>


            <p
              className={
                styles.heroDescription
              }
            >
              RippleProof traces a business-policy
              change through documents, chatbots,
              forms and backend behaviour, proposes
              repairs, keeps a human in control and
              produces executable evidence that the
              organization now follows the new rule.
            </p>


            <div
              className={
                styles.heroActions
              }
            >
              <Link
                href="/custom"
                className={
                  styles.primaryButton
                }
              >
                <ScanSearch
                  size={18}
                />

                Analyze a policy

                <ArrowRight
                  size={17}
                />
              </Link>


              <Link
                href="/runs"
                className={
                  styles.secondaryButton
                }
              >
                <History
                  size={17}
                />

                View run history
              </Link>
            </div>


            <div
              className={
                styles.trustRow
              }
            >
              <span>
                <CheckCircle2
                  size={14}
                />
                Human-in-the-loop
              </span>

              <span>
                <CheckCircle2
                  size={14}
                />
                PostgreSQL audit trail
              </span>

              <span>
                <CheckCircle2
                  size={14}
                />
                Deterministic verification
              </span>
            </div>
          </div>


          <div
            className={
              styles.heroVisual
            }
          >
            <div
              className={
                styles.visualHeader
              }
            >
              <div>
                <span
                  className={
                    styles.visualLabel
                  }
                >
                  POLICY CHANGE
                </span>

                <h2>
                  Customer Refund Policy
                </h2>
              </div>

              <span
                className={
                  styles.domainBadge
                }
              >
                FINANCIAL
              </span>
            </div>


            <div
              className={
                styles.ruleChange
              }
            >
              <div>
                <span>
                  PREVIOUS
                </span>

                <strong>
                  30
                  <small>
                    days
                  </small>
                </strong>
              </div>


              <div
                className={
                  styles.changeArrow
                }
              >
                <ArrowRight
                  size={28}
                />
              </div>


              <div>
                <span>
                  UPDATED
                </span>

                <strong>
                  14
                  <small>
                    days
                  </small>
                </strong>
              </div>
            </div>


            <div
              className={
                styles.contractBox
              }
            >
              <ShieldCheck
                size={20}
              />

              <div>
                <span>
                  Machine-verifiable contract
                </span>

                <code>
                  refund_period_days &lt;= 14
                </code>
              </div>
            </div>


            <div
              className={
                styles.pipeline
              }
            >
              <div
                className={
                  styles.pipelineItem
                }
              >
                <span
                  className={
                    styles.pipelineDotBlue
                  }
                />

                Semantic dependencies
              </div>

              <div
                className={
                  styles.pipelineLine
                }
              />

              <div
                className={
                  styles.pipelineItem
                }
              >
                <span
                  className={
                    styles.pipelineDotYellow
                  }
                />

                Human-reviewed patches
              </div>

              <div
                className={
                  styles.pipelineLine
                }
              />

              <div
                className={
                  styles.pipelineItem
                }
              >
                <span
                  className={
                    styles.pipelineDotGreen
                  }
                />

                Executable proof
              </div>
            </div>
          </div>
        </div>
      </section>


      <section
        className={
          styles.section
        }
      >
        <div
          className={
            styles.sectionHeading
          }
        >
          <span>
            THE PROBLEM
          </span>

          <h2>
            A policy rarely lives in one place.
          </h2>

          <p>
            A single business rule can be repeated
            across customer documentation, support
            prompts, forms, APIs and application
            logic. Updating the source document does
            not prove that the organization actually
            changed its behaviour.
          </p>
        </div>


        <div
          className={
            styles.problemGrid
          }
        >
          <article
            className={
              styles.problemCard
            }
          >
            <span>
              DOCUMENT
            </span>

            <strong>
              Policy says 14 days
            </strong>

            <div
              className={
                styles.goodStatus
              }
            >
              <CheckCircle2
                size={15}
              />

              Updated
            </div>
          </article>


          <article
            className={
              styles.problemCard
            }
          >
            <span>
              CHATBOT
            </span>

            <strong>
              Still tells users 30 days
            </strong>

            <div
              className={
                styles.staleStatus
              }
            >
              Drift detected
            </div>
          </article>


          <article
            className={
              styles.problemCard
            }
          >
            <span>
              FORM
            </span>

            <strong>
              Still accepts 30 days
            </strong>

            <div
              className={
                styles.staleStatus
              }
            >
              Drift detected
            </div>
          </article>


          <article
            className={
              styles.problemCard
            }
          >
            <span>
              API
            </span>

            <strong>
              Code still enforces 30 days
            </strong>

            <div
              className={
                styles.criticalStatus
              }
            >
              Critical
            </div>
          </article>
        </div>
      </section>


      <section
        className={
          `${styles.section} ${styles.workflowSection}`
        }
      >
        <div
          className={
            styles.sectionHeading
          }
        >
          <span>
            RIPPLEPROOF WORKFLOW
          </span>

          <h2>
            From policy change to proof.
          </h2>

          <p>
            The workflow combines semantic AI with
            deterministic software verification
            instead of asking an LLM to simply claim
            that everything is correct.
          </p>
        </div>


        <div
          className={
            styles.workflowGrid
          }
        >
          {workflow.map(
            ({
              number,
              title,
              description,
              icon: Icon,
            }) => (
              <article
                className={
                  styles.workflowCard
                }
                key={number}
              >
                <div
                  className={
                    styles.workflowTop
                  }
                >
                  <span
                    className={
                      styles.stepNumber
                    }
                  >
                    {number}
                  </span>

                  <span
                    className={
                      styles.stepIcon
                    }
                  >
                    <Icon
                      size={20}
                    />
                  </span>
                </div>

                <h3>
                  {title}
                </h3>

                <p>
                  {description}
                </p>
              </article>
            ),
          )}
        </div>
      </section>


      <section
        className={
          styles.section
        }
      >
        <div
          className={
            styles.sectionHeading
          }
        >
          <span>
            BUILT FOR TRUST
          </span>

          <h2>
            AI interprets. Software proves.
          </h2>
        </div>


        <div
          className={
            styles.capabilityGrid
          }
        >
          {capabilities.map(
            ({
              title,
              description,
              icon: Icon,
            }) => (
              <article
                key={title}
                className={
                  styles.capabilityCard
                }
              >
                <div
                  className={
                    styles.capabilityIcon
                  }
                >
                  <Icon
                    size={22}
                  />
                </div>

                <h3>
                  {title}
                </h3>

                <p>
                  {description}
                </p>
              </article>
            ),
          )}
        </div>
      </section>


      <section
        className={
          styles.evidenceSection
        }
      >
        <div
          className={
            styles.evidenceContent
          }
        >
          <div>
            <span
              className={
                styles.evidenceEyebrow
              }
            >
              <Workflow
                size={15}
              />

              EVIDENCE-FIRST ARCHITECTURE
            </span>

            <h2>
              Every decision leaves a trail.
            </h2>

            <p>
              Policy contracts, affected artifacts,
              findings, patch approvals,
              deterministic tests and verification
              receipts are persisted as auditable
              evidence.
            </p>
          </div>


          <div
            className={
              styles.evidenceStats
            }
          >
            <div>
              <strong>
                PostgreSQL
              </strong>
              <span>
                Persistent runs
              </span>
            </div>

            <div>
              <strong>
                Groq
              </strong>
              <span>
                Semantic reasoning
              </span>
            </div>

            <div>
              <strong>
                6/6
              </strong>
              <span>
                Boundary proof
              </span>
            </div>

            <div>
              <strong>
                SHA-256
              </strong>
              <span>
                Evidence receipt
              </span>
            </div>
          </div>
        </div>
      </section>


      <section
        className={
          styles.finalCta
        }
      >
        <div
          className={
            styles.ctaGlow
          }
        />

        <div>
          <span>
            READY TO TRACE THE RIPPLE?
          </span>

          <h2>
            Test a real policy change.
          </h2>

          <p>
            Upload organizational artifacts and
            see which surfaces still enforce the
            old rule.
          </p>
        </div>


        <div
          className={
            styles.ctaActions
          }
        >
          <Link
            href="/custom"
            className={
              styles.primaryButton
            }
          >
            <ScanSearch
              size={18}
            />

            Start analysis

            <ArrowRight
              size={17}
            />
          </Link>


          <Link
            href="/evaluation"
            className={
              styles.secondaryButton
            }
          >
            <FlaskConical
              size={17}
            />

            View evaluation
          </Link>
        </div>
      </section>
    </main>
  );
}