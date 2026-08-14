import type { APIRoute } from 'astro';
import { pb } from '../lib/pocketbase';

const site = 'https://bflex.by';

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toISOString().split('T')[0];
  } catch {
    return new Date().toISOString().split('T')[0];
  }
}

// Escape XML special characters
function esc(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

export const GET: APIRoute = async () => {
  const staticPages = [
    { url: '/', priority: '1.0', changefreq: 'weekly', lastmod: '' },
    { url: '/katalog/', priority: '0.9', changefreq: 'daily', lastmod: '' },
    { url: '/o-kompanii/', priority: '0.7', changefreq: 'monthly', lastmod: '' },
    { url: '/dokumenty/', priority: '0.7', changefreq: 'monthly', lastmod: '' },
    { url: '/dokumenty/tablica-khimicheskoy-stoykosti/', priority: '0.8', changefreq: 'monthly', lastmod: '' },
    { url: '/kontakty/', priority: '0.6', changefreq: 'monthly', lastmod: '' },
    { url: '/novosti/', priority: '0.8', changefreq: 'daily', lastmod: '' },
  ];

  let categoryUrls: any[] = [];
  let productUrls: any[] = [];
  let newsUrls: any[] = [];

  try {
    const categories = await pb.collection('categories').getFullList({
      filter: 'is_active=true',
      fields: 'id,slug,updated,parent',
    });

    const catMap = new Map(categories.map(c => [c.id, c]));

    categoryUrls = categories.map(cat => {
      const parent = cat.parent ? catMap.get(cat.parent) : null;
      const url = parent
        ? `/katalog/${parent.slug}/${cat.slug}/`
        : `/katalog/${cat.slug}/`;
      return { url, lastmod: formatDate(cat.updated), priority: parent ? '0.7' : '0.8', changefreq: 'weekly' };
    });

    const products = await pb.collection('products').getFullList({
      filter: 'is_active=true',
      expand: 'category',
      fields: 'slug,updated,expand',
    });

    productUrls = products.map(prod => {
      const cat = prod.expand?.category;
      const catParent = cat?.parent ? catMap.get(cat.parent) : null;
      const url = catParent
        ? `/katalog/${catParent.slug}/${cat.slug}/${prod.slug}/`
        : cat
        ? `/katalog/${cat.slug}/${prod.slug}/`
        : null;
      return url ? { url, lastmod: formatDate(prod.updated), priority: '0.6', changefreq: 'monthly' } : null;
    }).filter(Boolean);

    const news = await pb.collection('news').getFullList({
      filter: 'is_published=true',
      fields: 'slug,published_date',
    });
    newsUrls = news.map(n => ({
      url: `/novosti/${n.slug}/`,
      lastmod: formatDate(n.published_date),
      priority: '0.5',
      changefreq: 'monthly',
    }));
  } catch (e) {
    console.error('Sitemap generation error:', e);
  }

  const allPages = [...staticPages, ...categoryUrls, ...productUrls, ...newsUrls];

  const urlEntries = allPages.map(p => {
    const loc = esc(site + p.url);
    const lm = p.lastmod ? `\n    <lastmod>${p.lastmod}</lastmod>` : '';
    return `  <url>\n    <loc>${loc}</loc>${lm}\n    <changefreq>${p.changefreq}</changefreq>\n    <priority>${p.priority}</priority>\n  </url>`;
  }).join('\n');

  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urlEntries}\n</urlset>`;

  return new Response(xml, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8' },
  });
};
