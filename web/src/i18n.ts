import translations from "./en.json";
export type Language = "zh" | "en";
let language: Language = (() => {
  try {
    return localStorage.getItem("pysteps-3-language") === "zh" ? "zh" : "en";
  } catch {
    return "en";
  }
})();
export function getLanguage() {
  return language;
}
export function setLanguage(value: Language) {
  language = value;
  try {
    localStorage.setItem("pysteps-3-language", value);
  } catch {
    /* Preference is optional; learning data still uses SQLite. */
  }
}
const dictionary: Record<string, string> = translations;
const entries = Object.entries(dictionary).sort(
  (a, b) => b[0].length - a[0].length,
);
// Translate display text only. Identifiers, code, learner text and stored state are unchanged.
export function tr<T>(value: T): T {
  if (language !== "en") return value;
  if (Array.isArray(value)) return value.map((item) => tr(item)) as T;
  if (typeof value !== "string") return value;
  const normalized = value.replace(/\s+/g, " ").trim();
  if (dictionary[normalized]) return dictionary[normalized] as T;
  let result: string = value;
  for (const [chinese, english] of entries)
    if (chinese.length >= 2 && result.includes(chinese))
      result = result.split(chinese).join(english);
  return result as T;
}
