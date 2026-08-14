import type { APIRoute } from 'astro';
import { pb } from '../../lib/pocketbase';

export const GET: APIRoute = async ({ request }) => {
  const url = new URL(request.url);
  const page = parseInt(url.searchParams.get('page') || '1');
  const perPage = parseInt(url.searchParams.get('perPage') || '100');
  const search = url.searchParams.get('search') || '';

  try {
    const filter = search
      ? `chemical~"${search.replace(/"/g, '')}" && chemical!=""`
      : 'chemical!=""';
    
    const result = await pb.collection('chemical_resistance').getList(page, perPage, {
      sort: 'chemical',
      filter,
    });

    // Extract all unique material keys from first page for headers
    let materials: string[] = [];
    if (page === 1) {
      const allSample = await pb.collection('chemical_resistance').getList(1, 1, {
        filter: 'chemical!=""',
        sort: 'chemical',
      });
      if (allSample.items.length > 0 && allSample.items[0].resistance_data) {
        materials = Object.keys(allSample.items[0].resistance_data).sort();
      }
    }

    return new Response(JSON.stringify({
      items: result.items.filter(r => r.chemical?.trim()),
      totalItems: result.totalItems,
      totalPages: result.totalPages,
      page: result.page,
      materials: materials.length > 0 ? materials : undefined,
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (e) {
    return new Response(JSON.stringify({ items: [], totalItems: 0, totalPages: 0, page: 1, error: String(e) }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
