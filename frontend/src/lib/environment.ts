export type RuntimeEnvironmentKind = 'development' | 'production'

export interface RuntimeEnvironment {
  kind: RuntimeEnvironmentKind
  label: 'DEV' | 'PROD'
  caption: string
}

const DEVELOPMENT_VALUES = new Set(['dev', 'development', 'local'])
const PRODUCTION_VALUES = new Set(['prod', 'production'])

function normalizeEnvironmentValue(value: unknown): string {
  return typeof value === 'string' ? value.trim().toLowerCase() : ''
}

function resolveConfiguredEnvironment(values: unknown[]): RuntimeEnvironmentKind | null {
  for (const value of values) {
    const normalized = normalizeEnvironmentValue(value)
    if (DEVELOPMENT_VALUES.has(normalized)) return 'development'
    if (PRODUCTION_VALUES.has(normalized)) return 'production'
  }

  return null
}

function resolveEnvironmentKind(): RuntimeEnvironmentKind {
  const configuredEnvironment = resolveConfiguredEnvironment([
    import.meta.env.VITE_APP_ENV,
    import.meta.env.VITE_ENVIRONMENT,
  ])

  if (configuredEnvironment) return configuredEnvironment

  return import.meta.env.PROD ? 'production' : 'development'
}

export function getRuntimeEnvironment(): RuntimeEnvironment {
  const kind = resolveEnvironmentKind()

  if (kind === 'development') {
    return {
      kind,
      label: 'DEV',
      caption: 'Ambiente de desenvolvimento',
    }
  }

  return {
    kind,
    label: 'PROD',
    caption: 'Ambiente de produção',
  }
}
