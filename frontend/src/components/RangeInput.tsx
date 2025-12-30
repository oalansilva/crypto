import { Input } from './ui'

interface RangeInputProps {
    label: string
    min: string | number
    max: string | number
    step: string | number
    onMinChange: (val: string) => void
    onMaxChange: (val: string) => void
    onStepChange: (val: string) => void
}

export function RangeInput({ label, min, max, step, onMinChange, onMaxChange, onStepChange }: RangeInputProps) {
    return (
        <div className="space-y-2">
            <label className="text-xs text-[var(--text-secondary)] uppercase font-semibold">{label} (Range)</label>
            <div className="grid grid-cols-3 gap-2">
                <Input
                    type="number"
                    placeholder="Min"
                    value={min}
                    onChange={(e) => onMinChange(e.target.value)}
                    label="Mínimo"
                />
                <Input
                    type="number"
                    placeholder="Max"
                    value={max}
                    onChange={(e) => onMaxChange(e.target.value)}
                    label="Máximo"
                />
                <Input
                    type="number"
                    placeholder="Step"
                    value={step}
                    onChange={(e) => onStepChange(e.target.value)}
                    label="Passo"
                />
            </div>
        </div>
    )
}
