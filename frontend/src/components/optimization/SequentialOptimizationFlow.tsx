import React, { useState } from 'react';
import ParameterConfigScreen from './ParameterConfigScreen';
import SequentialOptimizationWizard from './SequentialOptimizationWizard';

interface SequentialOptimizationFlowProps {
    symbol: string;
    strategy: string;
    onComplete: (results: any) => void;
    onCancel: () => void;
}

const SequentialOptimizationFlow: React.FC<SequentialOptimizationFlowProps> = ({
    symbol,
    strategy,
    onComplete,
    onCancel
}) => {
    const [step, setStep] = useState<'config' | 'running'>('config');
    const [jobId, setJobId] = useState<string | null>(null);
    const [totalStages, setTotalStages] = useState(0);

    const handleStartOptimization = async (config: any) => {
        try {
            // Start optimization
            const response = await fetch('http://localhost:8000/api/optimize/sequential/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });

            if (!response.ok) {
                throw new Error('Failed to start optimization');
            }

            const data = await response.json();
            setJobId(data.job_id);
            setTotalStages(data.total_stages);
            setStep('running');
        } catch (error) {
            console.error('Error starting optimization:', error);
            alert('Failed to start optimization. Please try again.');
        }
    };

    const handleOptimizationComplete = (results: any) => {
        onComplete(results);
    };

    const handleCancelOptimization = () => {
        setStep('config');
        setJobId(null);
        onCancel();
    };

    if (step === 'config') {
        return (
            <ParameterConfigScreen
                symbol={symbol}
                strategy={strategy}
                onStart={handleStartOptimization}
                onCancel={onCancel}
            />
        );
    }

    if (step === 'running' && jobId) {
        return (
            <SequentialOptimizationWizard
                jobId={jobId}
                symbol={symbol}
                strategy={strategy}
                totalStages={totalStages}
                onComplete={handleOptimizationComplete}
                onCancel={handleCancelOptimization}
            />
        );
    }

    return null;
};

export default SequentialOptimizationFlow;
