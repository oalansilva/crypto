import { useEffect, useState } from 'react'
import { OnboardingGuide } from './OnboardingGuide'

const STORAGE_KEY = 'cripto-farol-onboarding-dismissed'

export function FirstUseOnboarding() {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    try {
      setVisible(window.localStorage.getItem(STORAGE_KEY) !== '1')
    } catch {
      setVisible(true)
    }
  }, [])

  const handleDismiss = () => {
    try {
      window.localStorage.setItem(STORAGE_KEY, '1')
    } catch {
      // Non-critical: Help remains available even if storage is blocked.
    }
    setVisible(false)
  }

  if (!visible) return null

  return <OnboardingGuide compact onDismiss={handleDismiss} />
}
