import type { APIRoute } from 'astro';
import { pb } from '../../lib/pocketbase';

export const POST: APIRoute = async ({ request }) => {
  try {
    const data = await request.formData();
    const name = data.get('name')?.toString() || '';
    const phone = data.get('phone')?.toString() || '';
    const company = data.get('company')?.toString() || '—';
    const message = data.get('message')?.toString() || '—';

    // Log request
    console.log('=== НОВАЯ ЗАЯВКА С САЙТА ===');
    console.log(`Имя: ${name}`);
    console.log(`Телефон: ${phone}`);
    console.log(`Организация: ${company}`);
    console.log(`Сообщение: ${message}`);
    console.log('============================');

    // Optionally save to PocketBase inquiries / contacts if collection exists
    try {
      await pb.collection('contacts').create({
        name,
        phone,
        company,
        message,
      });
    } catch {
      // If collection doesn't exist or requires auth, continue gracefully
    }

    return new Response(JSON.stringify({ ok: true, message: 'Заявка успешно отправлена' }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Contact form submission error:', error);
    return new Response(JSON.stringify({ ok: false, error: 'Ошибка при отправке заявки' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
