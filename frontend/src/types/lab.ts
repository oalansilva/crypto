export type LabLogLevel = 'INFO' | 'WARN' | 'ERROR' | 'DEBUG'

export interface LabLogEntry {
  timestamp: string
  level: LabLogLevel
  message: string
  step: string
  phase?: string
}

export type LogConnectionState = 'connecting' | 'connected' | 'error' | 'closed'

