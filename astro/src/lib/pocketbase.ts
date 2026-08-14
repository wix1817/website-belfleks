import PocketBase from 'pocketbase';

// Determine the URL based on environment variables or default to local dev server
const pbUrl = import.meta.env.PUBLIC_PB_URL || import.meta.env.PB_URL || 'http://127.0.0.1:8090';

export const pb = new PocketBase(pbUrl);

// Globally disable auto cancellation for SSR to prevent aborted requests on rapid sequential calls
pb.autoCancellation(false);
