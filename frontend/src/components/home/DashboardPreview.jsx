import React from 'react';
import { motion } from 'framer-motion';

function DashboardPreview() {
    return (
        <section className="gitintel-section" id="section-dashboard" style={{ perspective: '1600px' }}>
            <motion.h2 
                className="section-heading"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: false, amount: 0.4 }}
                transition={{ duration: 0.7 }}
            >
                Comprehensive Engineering Observability
            </motion.h2>
            
            <motion.div 
                className="dashboard-preview-container"
                initial={{ opacity: 0, y: 60, rotateX: 18, scale: 0.95 }}
                whileInView={{ opacity: 1, y: 0, rotateX: 0, scale: 1 }}
                viewport={{ once: false, amount: 0.2 }}
                transition={{ duration: 0.85, ease: [0.16, 1, 0.3, 1] }}
                style={{ 
                    transformStyle: 'preserve-3d'
                }}
            >
                <img 
                    src="/dashboard-preview.png" 
                    alt="GitIntel Dashboard — Risk analysis view showing bus factor, PR backlog, trend risk metrics and AI chat panel"
                    style={{ 
                        width: '100%', 
                        height: 'auto', 
                        borderRadius: '12px', 
                        display: 'block',
                        transform: 'translateZ(40px)',
                        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5), 0 0 60px rgba(0, 255, 255, 0.08)'
                    }}
                />
            </motion.div>
        </section>
    );
}

export default DashboardPreview;
