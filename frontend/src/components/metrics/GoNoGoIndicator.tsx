import React from 'react';
import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

interface CriteriaResult {
    status: 'GO' | 'NO-GO';
    reasons: string[];
    warnings: string[];
}

interface GoNoGoIndicatorProps {
    criteria: CriteriaResult;
}

export const GoNoGoIndicator: React.FC<GoNoGoIndicatorProps> = ({ criteria }) => {
    const isGo = criteria.status === 'GO';
    const hasWarnings = criteria.warnings && criteria.warnings.length > 0;

    return (
        <div className={`rounded-lg p-6 mb-6 ${isGo
                ? 'bg-gradient-to-r from-emerald-900/40 to-emerald-800/20 border border-emerald-500/30'
                : 'bg-gradient-to-r from-red-900/40 to-red-800/20 border border-red-500/30'
            }`}>
            <div className="flex items-center gap-3 mb-4">
                {isGo ? (
                    <CheckCircle className="w-8 h-8 text-emerald-400" />
                ) : (
                    <XCircle className="w-8 h-8 text-red-400" />
                )}
                <div>
                    <h2 className={`text-2xl font-bold ${isGo ? 'text-emerald-300' : 'text-red-300'}`}>
                        {isGo ? '✓ ESTRATÉGIA APROVADA' : '✗ ESTRATÉGIA REJEITADA'}
                    </h2>
                    <p className="text-sm text-gray-400 mt-1">
                        {isGo ? 'Esta estratégia atende aos critérios de qualidade' : 'Esta estratégia não atende aos critérios mínimos'}
                    </p>
                </div>
            </div>

            {/* Reasons */}
            {criteria.reasons && criteria.reasons.length > 0 && (
                <div className="space-y-2">
                    {criteria.reasons.map((reason, idx) => (
                        <div key={idx} className="flex items-start gap-2">
                            <span className={`text-lg ${isGo ? 'text-emerald-400' : 'text-red-400'}`}>
                                {isGo ? '✓' : '✗'}
                            </span>
                            <span className="text-sm text-gray-300">{reason}</span>
                        </div>
                    ))}
                </div>
            )}

            {/* Warnings */}
            {hasWarnings && (
                <div className="mt-4 pt-4 border-t border-yellow-500/20">
                    <div className="flex items-center gap-2 mb-2">
                        <AlertTriangle className="w-5 h-5 text-yellow-400" />
                        <span className="text-sm font-semibold text-yellow-300">Avisos</span>
                    </div>
                    <div className="space-y-2">
                        {criteria.warnings.map((warning, idx) => (
                            <div key={idx} className="flex items-start gap-2">
                                <span className="text-yellow-400">⚠</span>
                                <span className="text-sm text-gray-300">{warning}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};
