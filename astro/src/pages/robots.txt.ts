import type { APIRoute } from 'astro';

export const GET: APIRoute = () => {
  const content = `User-agent: *
Allow: /
Disallow: /api/
Disallow: /_/
Disallow: /admin

Sitemap: https://bflex.by/sitemap.xml
`;
  return new Response(content, {
    headers: { 'Content-Type': 'text/plain' }
  });
};
