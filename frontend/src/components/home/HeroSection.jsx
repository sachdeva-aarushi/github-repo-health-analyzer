import React from 'react';
import { motion } from 'framer-motion';

const textVar = {
    hidden:  { opacity: 0, y: 32 },
    visible: (i) => ({
        opacity: 1, y: 0,
        transition: { delay: i * 0.16, duration: 0.65, ease: [0.16, 1, 0.3, 1] },
    }),
};

function HeroSection({ owner, repo, setOwner, setRepo, handleSubmit }) {
    return (
        <section className="hero-section-3d" id="section-hero">
            {/* Dark overlay */}
            <div className="hero-bg-overlay" />

            {/* ── LEFT: headline + form ── */}
            <motion.div 
                className="hero-content"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
            >
                <motion.span className="overline hero-overline"
                    custom={0} initial="hidden" animate="visible" variants={textVar}>
                    REPOSITORY INTELLIGENCE PLATFORM
                </motion.span>

                <motion.h1 className="hero-headline"
                    custom={1} initial="hidden" animate="visible" variants={textVar}>
                    Understand your repositories{' '}
                    <span className="highlight-text">beyond</span> stars and forks.
                </motion.h1>

                <motion.p className="hero-subheadline"
                    custom={2} initial="hidden" animate="visible" variants={textVar}>
                    GitIntel combines deterministic analytics with AI-powered narration
                    to reveal maintainability risks, contributor bottlenecks, and
                    repository health in real time.
                </motion.p>

                <motion.form className="hero-form-container" onSubmit={handleSubmit}
                    custom={3} initial="hidden" animate="visible" variants={textVar}>
                    <div className="hero-form-inputs">
                        <input type="text" className="hero-input"
                            placeholder="Repository Owner"
                            value={owner} onChange={(e) => setOwner(e.target.value)} required />
                        <div className="hero-divider" />
                        <input type="text" className="hero-input"
                            placeholder="Repository Name"
                            value={repo} onChange={(e) => setRepo(e.target.value)} required />
                    </div>
                    <button type="submit" className="btn-primary btn-deep-blue">
                        Analyze Repository →
                    </button>
                </motion.form>
            </motion.div>

            {/* ── RIGHT: logo ── */}
            <motion.div 
                className="hero-visual"
                initial={{ opacity: 0, scale: 0.88, y: 40 }}
                animate={{ opacity: 1, scale: 1,    y: 0  }}
                transition={{ duration: 0.9, delay: 0.25, ease: [0.16, 1, 0.3, 1] }}
            >
                <div className="logo-glow-ring ring-outer" />
                <div className="logo-glow-ring ring-inner" />

                <div className="logo-cat-container">
                    <img src="/logo.png" alt="GitIntel"
                        className="hero-logo-img" draggable={false} />
                </div>
            </motion.div>
        </section>
    );
}

export default HeroSection;
