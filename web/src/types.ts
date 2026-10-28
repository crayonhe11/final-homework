export const CHAPTERS = ["条件判断", "循环", "函数与返回值"];
export type Concept = {
  topic: string;
  label: string;
  hint: string;
  order: number;
  prerequisites: string[];
};
export type Question = {
  id: string;
  topic: string;
  concept: string;
  difficulty: number;
  prompt: string;
  code: string;
  options: Record<string, string>;
  answer: string;
  explanation: string;
  hint: string;
  hints: string[];
  misconceptions: Partial<
    Record<string, { concept: string; evidence: string }>
  >;
};
export type Feedback = {
  concept: string;
  quote?: string;
  explanation: string;
  hint: string;
  source: "rule" | "ai";
  message: string;
  personalized?: boolean;
};
export type Attempt = {
  id: string;
  question_id: string;
  choice: string;
  reason: string;
  correct: boolean;
  diagnosis: string;
  created_at: string;
  hints_used: number;
  course_concept: string | null;
  feedback: Feedback;
};
export type CodeAttempt = {
  id: string;
  task_id: string;
  source: string;
  passed: boolean;
  created_at: string;
  details: string;
};
export type LearningState = {
  version: 1;
  reads: string[];
  attempts: Attempt[];
  drafts: Record<string, string>;
  codeAttempts: CodeAttempt[];
};
export const emptyState = (): LearningState => ({
  version: 1,
  reads: [],
  attempts: [],
  drafts: {},
  codeAttempts: [],
});

export type Summary = {
  courses: Record<
    string,
    {
      passed: boolean;
      locked: boolean;
      read: boolean;
      solved: number;
      latest: Record<string, boolean>;
    }
  >;
  schedule: Record<string, { due: number; stage: number }>;
};
export async function api(path: string, body?: unknown): Promise<any> {
  const response = await fetch(
    "/api/" + path,
    body === undefined
      ? {}
      : {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        },
  );
  const result = await response.json();
  if (!response.ok) throw Error(result.error || "服务器暂时不可用");
  return result;
}

export function uid(): string {
  if (typeof crypto.randomUUID === "function") return crypto.randomUUID();
  const b = crypto.getRandomValues(new Uint8Array(16));
  b[6] = (b[6] & 15) | 64;
  b[8] = (b[8] & 63) | 128;
  return Array.from(
    b,
    (v, i) =>
      ([4, 6, 8, 10].includes(i) ? "-" : "") + v.toString(16).padStart(2, "0"),
  ).join("");
}
