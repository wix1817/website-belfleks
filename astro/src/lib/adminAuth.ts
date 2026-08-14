import PocketBase from 'pocketbase';

export interface Manager {
  id: string;
  email: string;
  name?: string;
  avatar?: string;
  role?: 'admin' | 'manager' | 'editor' | string;
  collectionName: string;
  created?: string;
  updated?: string;
}

export const PB_URL = import.meta.env.PUBLIC_PB_URL || 'http://127.0.0.1:8090';

/**
 * Creates a PocketBase client instance loaded with the request's auth cookie
 */
export function createAdminPb(cookieHeader?: string): PocketBase {
  const pb = new PocketBase(PB_URL);
  if (cookieHeader) {
    pb.authStore.loadFromCookie(cookieHeader);
  }
  return pb;
}

/**
 * Checks if the current authStore has a valid session from the 'managers' collection
 */
export function isAdminAuthenticated(pbInstance: PocketBase): boolean {
  if (!pbInstance.authStore.isValid) return false;
  const model = pbInstance.authStore.record as any;
  if (!model) return false;
  return model.collectionName === 'managers' || model.collectionId === 'pbc_2468684168';
}

/**
 * Returns the current authenticated manager data or null
 */
export function getCurrentManager(pbInstance: PocketBase): Manager | null {
  if (!isAdminAuthenticated(pbInstance)) return null;
  const record = pbInstance.authStore.record as any;
  if (!record) return null;
  return {
    id: record.id,
    email: record.email,
    name: record.name || record.email.split('@')[0],
    avatar: record.avatar || '',
    role: record.role || 'manager',
    collectionName: record.collectionName || 'managers',
    created: record.created,
    updated: record.updated,
  };
}

/**
 * Server-side guard for Astro pages: redirects to /manage/ if not authenticated
 */
export function requireAuth(astro: { request: Request; redirect: (path: string, status?: number) => Response }): { pb: PocketBase; manager: Manager } | Response {
  const cookie = astro.request.headers.get('cookie') || '';
  const pb = createAdminPb(cookie);
  const manager = getCurrentManager(pb);

  if (!manager) {
    return astro.redirect('/manage/');
  }

  return { pb, manager };
}

/**
 * Client-side logout helper: clears authStore, deletes cookie and redirects to /manage/
 */
export function logout(targetUrl = '/manage/'): void {
  if (typeof window !== 'undefined') {
    // Clear cookies
    document.cookie = 'pb_auth=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT; SameSite=Lax;';
    localStorage.removeItem('pocketbase_auth');
    sessionStorage.removeItem('pocketbase_auth');
    window.location.href = targetUrl;
  }
}
