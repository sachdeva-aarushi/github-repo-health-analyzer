import React from 'react';
import { motion } from 'framer-motion';

function AISection() {
    return (
        <section className="gitintel-section ai-section" id="section-ai">
            <motion.div 
                className="ai-content"
                initial={{ opacity: 0, scale: 0.92, y: 30 }}
                whileInView={{ opacity: 1, scale: 1, y: 0 }}
                viewport={{ once: false, amount: 0.3 }}
                transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            >
                <h2>Not a generic chatbot. An engineering intelligence layer.</h2>
                <p>
                    GitIntel separates deterministic repository analytics from AI interpretation
                    to ensure accurate metrics, explainable insights, and architect-level
                    repository narration.
                </p>
            </motion.div>
        </section>
    );
}

export default AISection;
