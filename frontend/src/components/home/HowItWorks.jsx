import React from 'react';
import { motion } from 'framer-motion';

const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: { staggerChildren: 0.2 }
    }
};

const stepVariants = {
    hidden: { opacity: 0, y: 50, scale: 0.94 },
    visible: {
        opacity: 1,
        y: 0,
        scale: 1,
        transition: { duration: 0.7, ease: [0.16, 1, 0.3, 1] }
    }
};

function HowItWorks() {
    const steps = [
        { 
            step: 1, 
            title: 'Connect', 
            desc: 'Paste any public GitHub repository owner and name — no auth required.'
        },
        { 
            step: 2, 
            title: 'Analyze', 
            desc: 'Our AI dives deep to understand structure, patterns, and risks across your entire history.'
        },
        { 
            step: 3, 
            title: 'Get Insights', 
            desc: 'Receive actionable insights and senior-engineer-level recommendations to improve your code.'
        },
    ];

    return (
        <section className="gitintel-section section-split-how" id="section-howitworks">
            <motion.div 
                className="section-intro"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: false, amount: 0.4 }}
                transition={{ duration: 0.7 }}
            >
                <span className="overline">HOW IT WORKS</span>
                <h2>Understand your code in 3 <span className="highlight-text">deep</span> steps</h2>
            </motion.div>

            <motion.div 
                className="steps-container" 
                style={{ perspective: '1200px' }}
                variants={containerVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: false, amount: 0.25 }}
            >
                {/* Dynamically drawing connection line when snapped into view */}
                <motion.div 
                    className="steps-connector" 
                    initial={{ scaleX: 0 }}
                    whileInView={{ scaleX: 1 }}
                    viewport={{ once: false }}
                    transition={{ duration: 0.8, delay: 0.3, ease: 'easeInOut' }}
                    style={{ 
                        transformOrigin: 'left',
                        background: 'linear-gradient(90deg, var(--accent-primary) 0%, var(--accent-secondary) 100%)',
                        height: '2px',
                        boxShadow: '0 0 10px rgba(95,225,255,0.5)'
                    }} 
                />
                
                {steps.map((s, idx) => (
                    <motion.div 
                        key={idx} 
                        className="glass-card step-item"
                        variants={stepVariants}
                        whileHover={{ 
                            y: -8, 
                            scale: 1.03,
                            boxShadow: '0 20px 40px rgba(0,0,0,0.3), 0 0 30px rgba(95,225,255,0.15)',
                            borderColor: 'var(--accent-primary)'
                        }}
                        transition={{ type: 'spring', stiffness: 140, damping: 12 }}
                    >
                        <div className="step-number">
                            {s.step}
                        </div>
                        <h3>{s.title}</h3>
                        <p>{s.desc}</p>
                    </motion.div>
                ))}
            </motion.div>
        </section>
    );
}

export default HowItWorks;
