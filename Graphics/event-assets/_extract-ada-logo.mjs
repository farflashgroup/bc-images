import fs from "node:fs";

const htmlPath =
  "C:/Users/lfara/.cursor/projects/c-Users-lfara-OneDrive-Desktop-Development-BC-Images/agent-tools/d259e295-0026-4ab8-a719-a3e3392206e4.txt";
const outPath = new URL("./ada-cx-logo-official.svg", import.meta.url);

const h = fs.readFileSync(htmlPath, "utf8");
const m = h.match(/<svg viewBox="0 0 71 20"[\s\S]*?<\/svg>/);
if (!m) {
  console.error("no svg match");
  process.exit(1);
}
let s = m[0];
s = s.replace(/fill="#0A0B0C"/g, 'fill="#EDEAE4"');
s = s.replace(/<title>[^<]*<\/title>/, "<title>Ada CX</title>");
s = s.replace(/\sclass="[^"]*"/g, "");
fs.writeFileSync(outPath, s.trim() + "\n");
console.log("wrote", outPath.pathname, s.length);
