import React from 'react';
import { motion } from 'framer-motion';

const gridVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: { staggerChildren: 0.12 }
    }
};

const cardVariants = {
    hidden: { opacity: 0, y: 40, scale: 0.94 },
    visible: {
        opacity: 1,
        y: 0,
        scale: 1,
        transition: { duration: 0.65, ease: [0.16, 1, 0.3, 1] }
    }
};

function FeaturesSection() {
    const features = [
        {
            title: 'Deterministic Health Scoring',
            desc: 'Calculate exact metrics for code churn, issue resolution rates, and PR velocity.',
            icon: <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12" /></svg>,
        },
        {
            title: 'Contributor Risk Analysis',
            desc: 'Identify single points of failure, bus factor, and key contributor dependency.',
            icon: <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></svg>,
        },
        {
            title: 'Repository Structure Analysis',
            desc: 'Visualize and evaluate the modularity and maintainability of your architecture.',
            icon: <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" /><rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" /></svg>,
        },
        {
            title: 'Evolution Tracking',
            desc: 'Observe how your repository health changes over time to catch degradation early.',
            icon: <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18" /><polyline points="17 6 23 6 23 12" /></svg>,
        },
    ];

    return (
        <section className="gitintel-section section-stacked" id="section-features">
            <motion.div 
                className="section-intro-full"
                initial={{ opacity: 0, y: -20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: false, amount: 0.3 }}
                transition={{ duration: 0.7 }}
            >
                <span className="overline">POWERED BY ADVANCED AI</span>
                <h2>Everything you need to <span className="highlight-text">understand</span> your codebase</h2>
                <p>GitIntel and advanced analytics work together to give you deep insights across your entire repository.</p>
            </motion.div>
            
            <motion.div 
                className="features-grid-4col" 
                style={{ perspective: '1200px' }}
                variants={gridVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: false, amount: 0.2 }}
            >
                {features.map((f, idx) => (
                    <motion.div 
                        key={idx} 
                        className="glass-card feature-card"
                        variants={cardVariants}
                        whileHover={{ 
                            y: -8, 
                            scale: 1.02, 
                            rotateY: 6, 
                            rotateX: 3,
                            boxShadow: '0 24px 48px rgba(0,0,0,0.35), 0 0 40px rgba(95,225,255,0.25)',
                            borderColor: 'var(--accent-primary)'
                        }}
                        transition={{ type: 'spring', stiffness: 120, damping: 14 }}
                    >
                        <div className="feature-icon">{f.icon}</div>
                        <div className="feature-content">
                            <h3>{f.title}</h3>
                            <p>{f.desc}</p>
                        </div>
                    </motion.div>
                ))}
            </motion.div>
        </section>
    );
}

export default FeaturesSection;
