import { useState, lazy, Suspense } from 'react';
import { useNavigate } from 'react-router-dom';
import '../components/home/Home.css';

import HeroSection       from '../components/home/HeroSection';
import FeaturesSection   from '../components/home/FeaturesSection';
import HowItWorks        from '../components/home/HowItWorks';
import AISection         from '../components/home/AISection';
import DashboardPreview  from '../components/home/DashboardPreview';
import FinalCTA          from '../components/home/FinalCTA';
import Footer            from '../components/home/Footer';

const OrnamentalDust = lazy(() => import('../components/home/OrnamentalDust'));

function Home() {
    const [owner, setOwner] = useState('');
    const [repo,  setRepo]  = useState('');
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!owner.trim() || !repo.trim()) return;
        navigate(`/dashboard?owner=${encodeURIComponent(owner.trim())}&repo=${encodeURIComponent(repo.trim())}`);
    };

    return (
        <div className="gitintel-home">
            {/* Three.js blue dust particles */}
            <Suspense fallback={null}>
                <OrnamentalDust />
            </Suspense>

            <HeroSection
                owner={owner} repo={repo}
                setOwner={setOwner} setRepo={setRepo}
                handleSubmit={handleSubmit} />
            <FeaturesSection />
            <HowItWorks />
            <AISection />
            <DashboardPreview />
            <FinalCTA />
            <Footer />
        </div>
    );
}

export default Home;
