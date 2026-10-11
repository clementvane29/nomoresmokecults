import fs from "node:fs";
import path from "node:path";
import { marked } from "marked";

export interface Article {
  slug: string;
  title: string;
  category: string;
  date: string;
  readingTime: string;
  excerpt: string;
  author: string;
  authorRole: string;
  contentHtml: string;
  rawContent: string;
  tags: string[];
  jurisdiction?: string;
  target?: string;
}

const INVESTIGATIONS_DIR = path.resolve(process.cwd(), "../investigations");

export function getAllArticles(): Article[] {
  const articles: Article[] = [];

  function scan(dir: string, baseCat: string) {
    if (!fs.existsSync(dir)) return;
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        scan(fullPath, entry.name);
      } else if (entry.isFile() && entry.name.endsWith(".md") && !entry.name.startsWith("00_INDEX")) {
        const raw = fs.readFileSync(fullPath, "utf-8");
        const lines = raw.split("\n");
        let title = "";
        for (const line of lines) {
          if (line.startsWith("# ")) {
            title = line.replace("# ", "").trim();
            break;
          }
        }
        if (!title) {
          title = entry.name.replace(".md", "").replace(/_/g, " ");
        }

        // Clean slug
        const slug = entry.name.replace(".md", "").toLowerCase().replace(/_/g, "-");

        let category = "Investigations";
        let jurisdiction = "International";
        let target = "General";

        if (fullPath.includes("joe_brewer")) {
          category = "Benchmark Dossier";
          jurisdiction = "USA / Colombia";
          target = "Joseph Allen Brewer";
        } else if (fullPath.includes("global_dossiers")) {
          category = "Comparative Series";
          jurisdiction = "Global (USA/EU/LatAm)";
          target = "Eco-Cult Networks";
        } else if (fullPath.includes("target_dossiers")) {
          category = "Field Dossiers";
          jurisdiction = "Regional Hubs";
          target = "Regional Operators";
        } else if (entry.name.includes("GLOBAL_INVESTIGATION_ROSTER")) {
          category = "Global Intelligence";
          jurisdiction = "Multi-Jurisdictional";
          target = "Full Roster";
        }

        const words = raw.split(/\s+/).length;
        const minutes = Math.max(3, Math.round(words / 220));

        // Create excerpt
        let excerpt = "";
        for (const line of lines) {
          const l = line.trim();
          if (l && !l.startsWith("#") && !l.startsWith(">") && !l.startsWith("---") && !l.startsWith("|")) {
            excerpt = l.slice(0, 240) + "...";
            break;
          }
        }

        articles.push({
          slug,
          title,
          category,
          date: "August 31, 2026",
          readingTime: `${minutes} mins read`,
          excerpt: excerpt || "Forensic investigation & open-source analysis by Clement Vane.",
          author: "Clement Vane",
          authorRole: "Investigative Desk & Political Ecology",
          contentHtml: marked.parse(raw) as string,
          rawContent: raw,
          tags: ["Investigations", "Open-Source Intelligence", "Forensics", "Eco-Cults"],
          jurisdiction,
          target
        });
      }
    }
  }

  scan(INVESTIGATIONS_DIR, "");
  return articles;
}
