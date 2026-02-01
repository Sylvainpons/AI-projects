import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface MarkdownRendererProps {
  content: string;
}

export default function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        // Personnalisation des blocs de code
        code({ node, inline, className, children, ...props }: any) {
          const match = /language-(\w+)/.exec(className || '');
          return !inline && match ? (
            <div className="rounded-md overflow-hidden my-2 border border-zinc-700">
              <div className="bg-zinc-800 px-3 py-1 text-xs text-zinc-400 border-b border-zinc-700 flex justify-between">
                <span>{match[1]}</span>
                <span>Copy</span>
              </div>
              <SyntaxHighlighter
                style={vscDarkPlus}
                language={match[1]}
                PreTag="div"
                customStyle={{ margin: 0, padding: '1rem', background: '#1e1e1e' }}
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            </div>
          ) : (
            <code className="bg-zinc-800 text-zinc-200 px-1 py-0.5 rounded text-sm font-mono" {...props}>
              {children}
            </code>
          );
        },
        // Personnalisation des liens
        a: ({ node, ...props }) => <a className="text-blue-400 hover:underline" target="_blank" {...props} />,
        // Personnalisation des listes
        ul: ({ node, ...props }) => <ul className="list-disc pl-4 space-y-1 my-2" {...props} />,
        ol: ({ node, ...props }) => <ol className="list-decimal pl-4 space-y-1 my-2" {...props} />,
        // Titres
        h1: ({ node, ...props }) => <h1 className="text-xl font-bold mt-4 mb-2 text-zinc-100" {...props} />,
        h2: ({ node, ...props }) => <h2 className="text-lg font-bold mt-3 mb-2 text-zinc-100" {...props} />,
        p: ({ node, ...props }) => <p className="mb-2 leading-relaxed" {...props} />,
      }}
    >
      {content}
    </ReactMarkdown>
  );
}