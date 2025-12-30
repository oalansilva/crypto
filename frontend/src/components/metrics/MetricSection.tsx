import React, { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';

interface MetricSectionProps {
    title: string;
    icon?: React.ReactNode;
    children: React.ReactNode;
    defaultExpanded?: boolean;
}

export const MetricSection: React.FC<MetricSectionProps> = ({
    title,
    icon,
    children,
    defaultExpanded = false
}) => {
    const [isExpanded, setIsExpanded] = useState(defaultExpanded);

    return (
        <div className="border border-white/10 rounded-lg overflow-hidden mb-4">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full flex items-center justify-between p-4 bg-gray-800/40 hover:bg-gray-800/60 transition-colors"
            >
                <div className="flex items-center gap-3">
                    {icon}
                    <h3 className="text-lg font-semibold text-gray-200">{title}</h3>
                </div>
                {isExpanded ? (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                ) : (
                    <ChevronRight className="w-5 h-5 text-gray-400" />
                )}
            </button>

            {isExpanded && (
                <div className="p-4 bg-gray-900/20">
                    {children}
                </div>
            )}
        </div>
    );
};
