import React, { Suspense, useMemo, useRef } from 'react';
import { Canvas, useLoader } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera ,axesHelper} from '@react-three/drei';
import * as THREE from 'three';
import { PLYLoader } from 'three/examples/jsm/loaders/PLYLoader';
import samplePLY from '../../assets/3DPointCloud/sample.ply';
import { MathUtils } from 'three';

const ThickAxes = () => {
    const axisLength = 0.05;
    const axisThickness = 0.005;

    return (
        <group>
            {/* X Axis - Red */}
            <mesh position={[axisLength / 2, 0, 0]}>
                <boxGeometry args={[axisLength, axisThickness, axisThickness]} />
                <meshBasicMaterial color="red" />
            </mesh>

            {/* Y Axis - Green */}
            <mesh position={[0, axisLength / 2, 0]}>
                <boxGeometry args={[axisThickness, axisLength, axisThickness]} />
                <meshBasicMaterial color="green" />
            </mesh>

            {/* Z Axis - Blue */}
            <mesh position={[0, 0, axisLength / 2]}>
                <boxGeometry args={[axisThickness, axisThickness, axisLength]} />
                <meshBasicMaterial color="blue" />
            </mesh>
        </group>
    );
};
const ThickArrowAxes = () => {
    const axisLength = 0.02;
    const axisRadius = 0.002;
    const headLength = 0.02;
    const headRadius = 0.005;
    const offset_x=-0.05;
    const offset_y=0.0;
    const offset_z=-0.15;
    return (
        <group>
            {/* X Axis - Red */}
            <group rotation={[0, 0, -Math.PI / 2]}>
                {/* Shaft */}
                <mesh position={[-offset_y, offset_x+axisLength / 2, offset_z]}>
                    <cylinderGeometry args={[axisRadius, axisRadius, axisLength]} />
                    <meshBasicMaterial color="red" />
                </mesh>
                {/* Arrowhead */}
                <mesh position={[-offset_y, offset_x+axisLength + headLength / 2,offset_z]}>
                    <cylinderGeometry args={[0, headRadius, headLength]} />
                    <meshBasicMaterial color="red" />
                </mesh>
            </group>

            {/* Y Axis - Green */}
            <group>
                {/* Shaft */}
                <mesh position={[offset_x+0, offset_y+axisLength / 2, offset_z+0]}>
                    <cylinderGeometry args={[axisRadius, axisRadius, axisLength]} />
                    <meshBasicMaterial color="green" />
                </mesh>
                {/* Arrowhead */}
                <mesh position={[offset_x+0, offset_y+axisLength + headLength / 2,offset_z+ 0]}>
                    <cylinderGeometry args={[0, headRadius, headLength]} />
                    <meshBasicMaterial color="green" />
                </mesh>
            </group>

            {/* Z Axis - Blue */}
            <group rotation={[Math.PI / 2, 0, 0]}>
                {/* Shaft */}
                <mesh position={[offset_x+0, offset_z+axisLength / 2, -offset_y]}>
                    <cylinderGeometry args={[axisRadius, axisRadius, axisLength]} />
                    <meshBasicMaterial color="blue" />
                </mesh>
                {/* Arrowhead */}
                <mesh position={[offset_x+0, offset_z+axisLength + headLength / 2, -offset_y]}>
                    <cylinderGeometry args={[0, headRadius, headLength]} />
                    <meshBasicMaterial color="blue" />
                </mesh>
            </group>
        </group>
    );
};
const PLYMesh = () => {
    const rawGeometry = useLoader(PLYLoader, samplePLY);
    // console.log('PLY geometry loaded:', rawGeometry);
    // console.log('Positions count:', rawGeometry.attributes.position.count);
    const cachedGeometry = useRef(null);

    const geometry = useMemo(() => {
        if (cachedGeometry.current) return cachedGeometry.current;

        const geom = rawGeometry.clone();
        geom.computeVertexNormals();
        geom.center();

        if (geom.hasAttribute('color')) {
            const colors = geom.attributes.color;
            const color = new Float32Array(colors.count * 3);
            for (let i = 0; i < colors.count; i++) {
                color[i * 3] = colors.getX(i);
                color[i * 3 + 1] = colors.getY(i);
                color[i * 3 + 2] = colors.getZ(i);
            }
            geom.setAttribute('color', new THREE.BufferAttribute(color, 3));
        }

        cachedGeometry.current = geom;
        return geom;
    }, [rawGeometry]);

    return (
        <points geometry={geometry}>
            <pointsMaterial
                size={0.001}
                vertexColors={true}
                color={geometry.hasAttribute('color') ? undefined : 'orange'}
            />
        </points>
    );
};

const Scene = () => {
    return (
        <>
            <ambientLight intensity={1.0} />
            <directionalLight position={[3, 3, 3]} />
            <PerspectiveCamera makeDefault
                position={[0, 0, 1]}
                fov={75} />
 <ThickArrowAxes />
            <Suspense fallback={null}>
                <PLYMesh />
            </Suspense>
            <OrbitControls />
        </>
    );
};

const PLYViewer = () => {
    return (
        <Canvas style={{ height: '100vh', width: '100vw' }}>
            <Scene />
        </Canvas>
    );
};

export default PLYViewer;
