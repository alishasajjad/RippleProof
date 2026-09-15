const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  'http://127.0.0.1:8000';


export interface RunSummary {
  id: string;
  run_id?: string;
  policy_name?: string;
  status: string;
  risk_score?: number;
  semantic_mode?: string;
  llm_model?: string | null;
  created_at?: string | null;
}


export interface DashboardMetrics {
  total_runs: number;
  verified_runs: number;
  impact_ready_runs: number;
  approved_runs: number;
  artifacts_examined: number;
  stale_findings: number;
  critical_findings: number;
  patches_generated: number;
  approved_patches: number;
  average_risk: number;
  verification_success_rate: number;
  patch_approval_rate: number;
}


export interface DashboardResponse {
  metrics: DashboardMetrics;
  recent_runs: RunSummary[];
}


export interface BenchmarkScenario {
  name: string;
  domain: string;
  old_value: number;
  new_value: number;
  unit: string;

  before: {
    passed: number;
    failed: number;
    total: number;
    verified: boolean;
  };

  after: {
    passed: number;
    failed: number;
    total: number;
    verified: boolean;
  };
}


export interface BenchmarkResponse {
  benchmark_name: string;
  uses_llm: boolean;
  scenarios: number;

  before: {
    tests: number;
    passed: number;
    pass_rate: number;
  };

  after: {
    tests: number;
    passed: number;
    pass_rate: number;
  };

  improvement_points: number;

  results: BenchmarkScenario[];
}


export interface EvaluationResponse {
  operational: DashboardMetrics;

  benchmark: {
    name: string;
    scenarios: number;
    before_pass_rate: number;
    after_pass_rate: number;
    improvement_points: number;
    uses_llm: boolean;
  };
}


export interface RunDetail {
  id?: string;
  run_id?: string;
  policy_name?: string;
  status?: string;
  risk_score?: number;
  semantic_mode?: string;
  llm_model?: string | null;
  created_at?: string | null;

  contract?: Record<
    string,
    unknown
  >;

  contract_json?: Record<
    string,
    unknown
  >;

  artifacts?: Array<
    Record<
      string,
      unknown
    >
  >;

  findings?: Array<
    Record<
      string,
      unknown
    >
  >;

  patches?: Array<
    Record<
      string,
      unknown
    >
  >;

  verification_tests?: Array<
    Record<
      string,
      unknown
    >
  >;

  events?: Array<
    Record<
      string,
      unknown
    >
  >;
}


async function request<T>(
  path: string,
): Promise<T> {

  const response =
    await fetch(
      `${API_URL}${path}`,
      {
        cache:
          'no-store',
      }
    );


  const data =
    await response.json();


  if (!response.ok) {

    throw new Error(
      data.detail ??
      `Request failed: ${response.status}`
    );
  }


  const typedData: T =
    data;


  return typedData;
}


export function getDashboard():
Promise<DashboardResponse> {

  return request<
    DashboardResponse
  >(
    '/api/dashboard/summary'
  );
}


export function getRuns():
Promise<RunSummary[]> {

  return request<
    RunSummary[]
  >(
    '/api/runs'
  );
}


export function getRunDetail(
  runId: string,
):
Promise<RunDetail> {

  return request<
    RunDetail
  >(
    `/api/runs/${runId}`
  );
}


export function getEvaluation():
Promise<EvaluationResponse> {

  return request<
    EvaluationResponse
  >(
    '/api/evaluation/summary'
  );
}


export function getBenchmark():
Promise<BenchmarkResponse> {

  return request<
    BenchmarkResponse
  >(
    '/api/evaluation/benchmark'
  );
}