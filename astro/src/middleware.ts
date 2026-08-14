import { defineMiddleware } from 'astro:middleware';
import { createAdminPb, isAdminAuthenticated, getCurrentManager } from './lib/adminAuth';

export const onRequest = defineMiddleware(async (context, next) => {
  const url = new URL(context.request.url);
  const pathname = url.pathname.replace(/\/$/, '') || '/';

  // Only handle /manage routes
  if (pathname.startsWith('/manage')) {
    const cookie = context.request.headers.get('cookie') || '';
    const pb = createAdminPb(cookie);
    const isAuth = isAdminAuthenticated(pb);
    const manager = getCurrentManager(pb);

    context.locals.pb = pb;
    context.locals.manager = manager;

    // Login page: if already authenticated, redirect to /manage/dashboard
    if (pathname === '/manage') {
      if (isAuth) {
        return context.redirect('/manage/dashboard');
      }
      return next();
    }

    // Protected admin routes: if not authenticated, redirect to /manage/
    if (!isAuth) {
      return context.redirect('/manage/');
    }
  }

  return next();
});
