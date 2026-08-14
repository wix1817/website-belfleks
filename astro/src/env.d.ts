/// <reference path="../.astro/types.d.ts" />
/// <reference types="astro/client" />

declare namespace App {
  interface Locals {
    manager?: import('./lib/adminAuth').Manager | null;
    pb?: import('pocketbase').default;
  }
}
