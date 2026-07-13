import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { RouterProvider } from '@tanstack/react-router'
import { router } from './router'
import { queryClient } from './lib/query-client'
import './styles.css'

// `npm run dev:mock` sets VITE_MOCKS, which swaps the backend for an MSW
// service worker serving faker data (see src/mocks/). The dynamic import
// keeps msw + faker out of the bundle everywhere else — Vite inlines the
// env var at build time, so production builds drop this branch entirely.
async function enableMocking() {
  if (import.meta.env.VITE_MOCKS !== 'true') return
  const { worker } = await import('./mocks/browser')
  return worker.start({
    onUnhandledRequest(request, print) {
      // Only warn about API calls we forgot to mock; ignore assets/HMR.
      if (new URL(request.url).pathname.startsWith('/api/')) print.warning()
    },
  })
}

enableMocking().then(() => {
  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </React.StrictMode>,
  )
})
