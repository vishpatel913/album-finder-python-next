import {
  createRootRoute,
  createRoute,
  createRouter,
  Link,
  Outlet,
} from '@tanstack/react-router'
import { AlbumsPage } from './routes/albums'
import { AlbumDetailPage } from './routes/album-detail'

// Code-based routing keeps the whole route tree visible in one file — no
// codegen step. If this grows, TanStack's file-based routing is the upgrade.
const rootRoute = createRootRoute({ component: RootLayout })

function RootLayout() {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <header className="border-b border-zinc-800">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <Link to="/" className="text-lg font-semibold">
            Album Finder
          </Link>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  )
}

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: AlbumsPage,
})

const albumRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/album/$albumId',
  component: AlbumDetailPage,
})

const routeTree = rootRoute.addChildren([indexRoute, albumRoute])

export const router = createRouter({ routeTree })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
