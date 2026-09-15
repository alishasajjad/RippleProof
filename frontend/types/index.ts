export type Severity =
  | 'low'
  | 'medium'
  | 'high'
  | 'critical';

export type FindingStatus =
  | 'compliant'
  | 'stale'
  | 'unknown';


export interface PolicyRule {
  field: string;
  operator: string;
  value: number | string;
  unit?: string | null;
}


export interface PolicyContract {
  policy_name: string;
  subject: string;
  attribute: string;

  old_rule: PolicyRule;
  new_rule: PolicyRule;

  change_type: string;
  risk_domain: string;

  boundary_values: number[];
}


export interface Artifact {
  id: string;
  name: string;

  artifact_type:
    | 'DOCUMENT'
    | 'WEBSITE'
    | 'CHATBOT'
    | 'FORM'
    | 'API'
    | 'CODE';

  content: string;
  relationship: string;

  source_path?: string | null;
}


export interface ImpactFinding {
  artifact_id: string;
  artifact_name: string;

  affected: boolean;

  severity: Severity;

  confidence: number;

  relationship: string;

  evidence: string;

  reason: string;

  status: FindingStatus;
}


export interface PatchProposal {
  artifact_id: string;
  artifact_name: string;

  original_content: string;
  proposed_content: string;

  diff: string;
  rationale: string;

  status:
    | 'proposed'
    | 'approved'
    | 'rejected';
}


export interface VerificationCase {
  name: string;

  input: Record<
    string,
    unknown
  >;

  expected: unknown;
  actual: unknown;

  passed: boolean;
}


export interface VerificationReport {
  total: number;
  passed: number;
  failed: number;

  cases: VerificationCase[];

  verified: boolean;
}


export interface ProofReceipt {
  policy_name: string;

  change_summary: string;

  artifacts_examined: number;

  affected_artifacts: number;

  confirmed_inconsistencies: number;

  critical_inconsistencies: number;

  approved_fixes: number;

  verification_tests: number;

  tests_passed: number;

  tests_failed: number;

  policy_coverage_percent: number;

  behavior_verification:
    | 'PASSED'
    | 'FAILED';

  evidence_hash: string;
}


export interface AnalysisResponse {
  run_id: string;

  engine: {
    semantic_mode:
      | 'llm'
      | 'deterministic_fallback';

    llm_model?:
      | string
      | null;

    database: string;

    risk_score: number;
  };

  request: {
    policy_name: string;
    old_text: string;
    new_text: string;
  };

  contract: PolicyContract;

  artifacts: Artifact[];

  findings: ImpactFinding[];

  patches: PatchProposal[];

  verification_before_fix:
    VerificationReport;
}


export interface VerifyResponse {
  run_id: string;

  verification_after_fix:
    VerificationReport;

  receipt: ProofReceipt;
}


export interface RunSummary {
  id: string;

  policy_name: string;

  status: string;

  risk_score: number;

  semantic_mode: string;

  llm_model?:
    | string
    | null;

  created_at: string;

  updated_at: string;
}


export interface RunDetail
  extends RunSummary {

  contract: PolicyContract;

  artifacts: Array<
    Artifact & {
      original_content: string;
      current_content: string;
    }
  >;

  impacts: ImpactFinding[];

  patches: Array<{
    id: string;
    artifact_id: string;
    status: string;
    diff: string;
    rationale: string;
  }>;

  verification_tests: Array<{
    name: string;

    input: Record<
      string,
      unknown
    >;

    expected: unknown;

    actual: unknown;

    passed: boolean;
  }>;

  events: Array<{
    event_type: string;

    actor: string;

    payload: Record<
      string,
      unknown
    >;

    created_at: string;
  }>;
}