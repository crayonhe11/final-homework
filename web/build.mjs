import { build } from "esbuild";
import { createHash } from "node:crypto";
import { mkdir, cp, writeFile, rm, readFile } from "node:fs/promises";
await rm("static", { recursive: true, force: true });
await mkdir("static/assets", { recursive: true });
await build({
  entryPoints: ["src/main.tsx"],
  bundle: true,
  minify: true,
  outfile: "static/assets/app.js",
  jsx: "automatic",
  target: ["es2022"],
  define: { "process.env.NODE_ENV": '"production"' },
  legalComments: "linked",
});
await cp("public", "static", { recursive: true });
const version = createHash("sha256")
  .update(await readFile("static/assets/app.js"))
  .update(await readFile("static/assets/app.css"))
  .digest("hex")
  .slice(0, 12);
await writeFile(
  "static/index.html",
  `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PySteps · Learn Python</title><link rel="icon" href="/favicon.svg"><link rel="stylesheet" href="/assets/app.css?v=${version}"></head><body><div id="root"></div><script type="module" src="/assets/app.js?v=${version}"></script></body></html>`,
);
console.log("网页已构建到web/static，可由python main.py直接提供。");
