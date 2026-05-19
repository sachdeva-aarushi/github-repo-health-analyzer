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
                <div style={{ transform: 'translateZ(40px)', textShadow: '0 8px 16px rgba(0,0,0,0.5)', fontSize: '1.25rem', fontWeight: 600 }}>
                    [ Dashboard UI Preview Placeholder ]
                </div>
            </motion.div>
        </section>
    );
}

export default DashboardPreview;
