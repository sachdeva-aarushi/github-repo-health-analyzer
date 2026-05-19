import React from 'react';
import { motion } from 'framer-motion';

function FinalCTA() {
    const scrollToTop = () => window.scrollTo({ top: 0, behavior: 'smooth' });

    return (
        <section className="gitintel-section cta-section" id="section-cta" style={{ overflow: 'hidden' }}>
            <motion.div 
                className="cta-content"
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: false, amount: 0.3 }}
                transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            >
                <h2>Ready to explore the <span className="highlight-text">depths</span> of your codebase?</h2>
                <p>Dive in and discover insights that help you build better, safer, and faster.</p>
                <motion.button className="btn-primary" onClick={scrollToTop}
                    whileHover={{ scale: 1.04, y: -2 }} whileTap={{ scale: 0.97 }}>
                    Get started for free &rarr;
                </motion.button>
            </motion.div>
            
            <motion.div 
                className="cta-visual-placeholder"
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: false, amount: 0.3 }}
                transition={{ duration: 0.8, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            />
        </section>
    );
}

export default FinalCTA;
