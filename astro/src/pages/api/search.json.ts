import type { APIRoute } from 'astro';
import { pb } from '../../lib/pocketbase';

export const GET: APIRoute = async ({ request }) => {
  const url = new URL(request.url);
  const q = url.searchParams.get('q')?.trim() || '';

  if (q.length < 3) {
    return new Response(JSON.stringify({ items: [] }), {
      headers: { 'Content-Type': 'application/json' }
    });
  }

  // Sanitize query to prevent PocketBase filter injection
  const safe = q.replace(/["\\]/g, '').substring(0, 100);

  try {
    const result = await pb.collection('products').getList(1, 8, {
      filter: `(name~"${safe}" || short_description~"${safe}" || tags~"${safe}") && is_active=true`,
      expand: 'category,category.parent',
      fields: 'id,name,slug,images,collectionId,expand,short_description',
      sort: '-is_featured,sort_order,name',
    });

    return new Response(JSON.stringify({ items: result.items }), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (e) {
    console.error('Search API error:', e);
    return new Response(JSON.stringify({ items: [], error: String(e) }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
