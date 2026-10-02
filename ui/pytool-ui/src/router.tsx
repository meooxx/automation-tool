import {
  createBrowserHistory,
  createMemoryHistory,
  createRouter as createTanStackRouter,
} from '@tanstack/react-router'
import { routeTree } from './routeTree.gen'

export function getRouter() {
  const router = createTanStackRouter({
    routeTree,
    history:
      typeof window === 'undefined'
        ? createMemoryHistory({ initialEntries: ['/'] })
        : createBrowserHistory(),
    scrollRestoration: true,
    defaultPreload: 'intent',
    defaultPreloadStaleTime: 0,
  })

  return router
}

declare module '@tanstack/react-router' {
  interface Register {
    router: ReturnType<typeof getRouter>
  }
}
