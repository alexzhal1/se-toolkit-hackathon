import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";

export default function Markdown({ children }: { children: string }) {
  // Normalize common LaTeX inline notation: ( ... ) and [ ... ] are not standard.
  // Convert ( \cmd ... ) -> $...$ and [ \cmd ... ] -> $$...$$
  const normalized = children
    .replace(/\\\(([^]+?)\\\)/g, (_, m) => `$${m}$`)
    .replace(/\\\[([^]+?)\\\]/g, (_, m) => `$$${m}$$`);

  return (
    <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
      {normalized}
    </ReactMarkdown>
  );
}
