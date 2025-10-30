// Scene setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });

renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Create canvas for procedural continent texture
function createContinentTexture() {
    const size = 1024;
    const canvas = document.createElement('canvas');
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');

    // Ocean color
    ctx.fillStyle = '#1a4d7a';
    ctx.fillRect(0, 0, size, size);

    // Generate continents using random blobs
    const continentCount = 5;
    const landColor = '#2d5a3d';
    const beachColor = '#c2b280';

    for (let i = 0; i < continentCount; i++) {
        const centerX = Math.random() * size;
        const centerY = Math.random() * size;
        const blobCount = 15 + Math.floor(Math.random() * 20);

        // Draw continent as collection of overlapping circles
        for (let j = 0; j < blobCount; j++) {
            const angle = Math.random() * Math.PI * 2;
            const distance = Math.random() * 150;
            const x = centerX + Math.cos(angle) * distance;
            const y = centerY + Math.sin(angle) * distance;
            const radius = 30 + Math.random() * 80;

            // Create gradient for more natural look
            const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
            gradient.addColorStop(0, landColor);
            gradient.addColorStop(0.7, landColor);
            gradient.addColorStop(1, '#1a4d7a');

            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(x, y, radius, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    // Add some smaller islands
    for (let i = 0; i < 20; i++) {
        const x = Math.random() * size;
        const y = Math.random() * size;
        const radius = 10 + Math.random() * 30;

        ctx.fillStyle = landColor;
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();
    }

    // Add polar ice caps
    const iceColor = '#e8f4f8';
    const polarHeight = size * 0.15;

    // North pole
    const northGradient = ctx.createLinearGradient(0, 0, 0, polarHeight);
    northGradient.addColorStop(0, iceColor);
    northGradient.addColorStop(1, 'transparent');
    ctx.fillStyle = northGradient;
    ctx.fillRect(0, 0, size, polarHeight);

    // South pole
    const southGradient = ctx.createLinearGradient(0, size, 0, size - polarHeight);
    southGradient.addColorStop(0, iceColor);
    southGradient.addColorStop(1, 'transparent');
    ctx.fillStyle = southGradient;
    ctx.fillRect(0, size - polarHeight, size, polarHeight);

    const texture = new THREE.CanvasTexture(canvas);
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.ClampToEdgeWrapping;

    return texture;
}

// Create planet sphere
const geometry = new THREE.SphereGeometry(2, 64, 64);
const texture = createContinentTexture();

const material = new THREE.MeshPhongMaterial({
    map: texture,
    shininess: 5
});

const planet = new THREE.Mesh(geometry, material);
scene.add(planet);

// Add atmosphere glow
const atmosphereGeometry = new THREE.SphereGeometry(2.1, 64, 64);
const atmosphereMaterial = new THREE.MeshBasicMaterial({
    color: 0x4488ff,
    transparent: true,
    opacity: 0.15,
    side: THREE.BackSide
});
const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
scene.add(atmosphere);

// Lighting setup
const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 3, 5);
scene.add(directionalLight);

// Add subtle rim light from opposite side
const rimLight = new THREE.DirectionalLight(0x6688ff, 0.3);
rimLight.position.set(-5, -2, -5);
scene.add(rimLight);

// Camera position
camera.position.z = 5;

// Add stars in background
const starsGeometry = new THREE.BufferGeometry();
const starsMaterial = new THREE.PointsMaterial({ color: 0xffffff, size: 0.02 });

const starsVertices = [];
for (let i = 0; i < 10000; i++) {
    const x = (Math.random() - 0.5) * 2000;
    const y = (Math.random() - 0.5) * 2000;
    const z = (Math.random() - 0.5) * 2000;
    starsVertices.push(x, y, z);
}

starsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starsVertices, 3));
const stars = new THREE.Points(starsGeometry, starsMaterial);
scene.add(stars);

// Create spaceship
const spaceship = new THREE.Group();

// Main body (fuselage)
const bodyGeometry = new THREE.ConeGeometry(0.08, 0.4, 8);
const bodyMaterial = new THREE.MeshPhongMaterial({
    color: 0xcccccc,
    shininess: 100,
    specular: 0x444444
});
const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
body.rotation.x = Math.PI / 2;
spaceship.add(body);

// Cockpit (glowing blue sphere)
const cockpitGeometry = new THREE.SphereGeometry(0.06, 16, 16);
const cockpitMaterial = new THREE.MeshPhongMaterial({
    color: 0x00ccff,
    emissive: 0x0088cc,
    shininess: 100,
    transparent: true,
    opacity: 0.9
});
const cockpit = new THREE.Mesh(cockpitGeometry, cockpitMaterial);
cockpit.position.z = 0.15;
spaceship.add(cockpit);

// Wings
const wingGeometry = new THREE.BoxGeometry(0.4, 0.02, 0.15);
const wingMaterial = new THREE.MeshPhongMaterial({
    color: 0x888888,
    shininess: 80
});
const leftWing = new THREE.Mesh(wingGeometry, wingMaterial);
leftWing.position.set(-0.15, 0, -0.05);
spaceship.add(leftWing);

const rightWing = new THREE.Mesh(wingGeometry, wingMaterial);
rightWing.position.set(0.15, 0, -0.05);
spaceship.add(rightWing);

// Engine glows (emissive spheres)
const engineGeometry = new THREE.SphereGeometry(0.04, 16, 16);
const engineMaterial = new THREE.MeshBasicMaterial({
    color: 0xff6600,
    transparent: true,
    opacity: 0.8
});

const leftEngine = new THREE.Mesh(engineGeometry, engineMaterial);
leftEngine.position.set(-0.06, 0, -0.2);
spaceship.add(leftEngine);

const rightEngine = new THREE.Mesh(engineGeometry, engineMaterial);
rightEngine.position.set(0.06, 0, -0.2);
spaceship.add(rightEngine);

// Add engine glow effect (point lights)
const leftEngineLight = new THREE.PointLight(0xff6600, 0.5, 1);
leftEngineLight.position.set(-0.06, 0, -0.2);
spaceship.add(leftEngineLight);

const rightEngineLight = new THREE.PointLight(0xff6600, 0.5, 1);
rightEngineLight.position.set(0.06, 0, -0.2);
spaceship.add(rightEngineLight);

// Add spotlight from front of spaceship
const spaceshipLight = new THREE.SpotLight(0x00ccff, 0.3);
spaceshipLight.position.set(0, 0, 0.2);
spaceshipLight.angle = Math.PI / 6;
spaceshipLight.penumbra = 0.5;
spaceship.add(spaceshipLight);

// Position spaceship in orbit
const orbitRadius = 3.5;
spaceship.position.x = orbitRadius;
spaceship.position.y = 0.5;

scene.add(spaceship);

// Orbit parameters
let orbitAngle = 0;
const orbitSpeed = 0.005;
const orbitTilt = 0.3; // Tilt the orbit for more dynamic view

// Animation loop
function animate() {
    requestAnimationFrame(animate);

    // Rotate planet
    planet.rotation.y += 0.002;
    atmosphere.rotation.y += 0.002;

    // Slow rotation of stars for depth
    stars.rotation.y += 0.0001;

    // Spaceship orbital motion
    orbitAngle += orbitSpeed;

    // Calculate orbital position with tilt
    spaceship.position.x = Math.cos(orbitAngle) * orbitRadius;
    spaceship.position.z = Math.sin(orbitAngle) * orbitRadius;
    spaceship.position.y = Math.sin(orbitAngle) * orbitTilt;

    // Make spaceship face direction of travel
    spaceship.lookAt(
        Math.cos(orbitAngle + 0.1) * orbitRadius,
        Math.sin(orbitAngle + 0.1) * orbitTilt,
        Math.sin(orbitAngle + 0.1) * orbitRadius
    );

    // Add slight roll to the spaceship
    spaceship.rotation.z = Math.sin(orbitAngle * 2) * 0.1;

    // Pulse the engine lights for effect
    const enginePulse = 0.3 + Math.sin(orbitAngle * 10) * 0.2;
    leftEngineLight.intensity = enginePulse;
    rightEngineLight.intensity = enginePulse;

    renderer.render(scene, camera);
}

// Handle window resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Start animation
animate();
