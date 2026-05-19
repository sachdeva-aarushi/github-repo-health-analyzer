import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

function DustParticles({ count = 220 }) {
    const pointsRef = useRef();

    const { positions, velocities } = useMemo(() => {
        const positions  = new Float32Array(count * 3);
        const velocities = new Float32Array(count * 2);
        for (let i = 0; i < count; i++) {
            positions[i * 3]     = (Math.random() - 0.5) * 24;
            positions[i * 3 + 1] = (Math.random() - 0.5) * 14;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 4;
            const speed = 0.002 + Math.random() * 0.007;
            const angle = Math.random() * Math.PI * 2;
            velocities[i * 2]     = Math.cos(angle) * speed;
            velocities[i * 2 + 1] = Math.sin(angle) * speed;
        }
        return { positions, velocities };
    }, [count]);

    useFrame(({ clock }) => {
        if (!pointsRef.current) return;
        const attr = pointsRef.current.geometry.attributes.position;
        const t    = clock.elapsedTime;
        for (let i = 0; i < count; i++) {
            attr.array[i * 3]     += velocities[i * 2];
            attr.array[i * 3 + 1] += velocities[i * 2 + 1] + Math.sin(t * 0.25 + i * 0.3) * 0.0005;
            if (attr.array[i * 3]     >  12) attr.array[i * 3]     = -12;
            if (attr.array[i * 3]     < -12) attr.array[i * 3]     =  12;
            if (attr.array[i * 3 + 1] >   7) attr.array[i * 3 + 1] =  -7;
            if (attr.array[i * 3 + 1] <  -7) attr.array[i * 3 + 1] =   7;
        }
        attr.needsUpdate = true;
    });

    return (
        <points ref={pointsRef}>
            <bufferGeometry>
                <bufferAttribute
                    attach="attributes-position"
                    count={count}
                    array={positions}
                    itemSize={3}
                />
            </bufferGeometry>
            <pointsMaterial
                size={0.06}
                color="#5FE1FF"
                transparent
                opacity={0.7}
                sizeAttenuation
                blending={THREE.AdditiveBlending}
                depthWrite={false}
            />
        </points>
    );
}

export default function OrnamentalDust() {
    return (
        <div style={{
            position: 'fixed', top: 0, left: 0,
            width: '100%', height: '100%',
            zIndex: 2, pointerEvents: 'none',
        }}>
            <Canvas
                camera={{ position: [0, 0, 8], fov: 70 }}
                dpr={[1, 1.5]}
                gl={{ antialias: false, alpha: true }}
                style={{ background: 'transparent' }}
            >
                <DustParticles count={220} />
            </Canvas>
        </div>
    );
}
