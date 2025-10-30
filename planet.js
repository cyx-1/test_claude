// Scene setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });

renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Create canvas for procedural Mars-like texture
function createContinentTexture() {
    const size = 1024;
    const canvas = document.createElement('canvas');
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');

    // Base Mars surface color (rusty red-orange)
    ctx.fillStyle = '#c1440e';
    ctx.fillRect(0, 0, size, size);

    // Generate darker basaltic plains (like Syrtis Major)
    const darkRegionCount = 7;
    const darkColor = '#8b4513';

    for (let i = 0; i < darkRegionCount; i++) {
        const centerX = Math.random() * size;
        const centerY = Math.random() * size;
        const blobCount = 12 + Math.floor(Math.random() * 15);

        // Draw dark regions as collection of overlapping circles
        for (let j = 0; j < blobCount; j++) {
            const angle = Math.random() * Math.PI * 2;
            const distance = Math.random() * 120;
            const x = centerX + Math.cos(angle) * distance;
            const y = centerY + Math.sin(angle) * distance;
            const radius = 25 + Math.random() * 60;

            // Create gradient for more natural look
            const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
            gradient.addColorStop(0, darkColor);
            gradient.addColorStop(0.7, darkColor);
            gradient.addColorStop(1, '#c1440e');

            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(x, y, radius, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    // Add lighter highland areas
    const lightRegionCount = 6;
    const lightColor = '#e8a87c';

    for (let i = 0; i < lightRegionCount; i++) {
        const centerX = Math.random() * size;
        const centerY = Math.random() * size;
        const blobCount = 10 + Math.floor(Math.random() * 12);

        for (let j = 0; j < blobCount; j++) {
            const angle = Math.random() * Math.PI * 2;
            const distance = Math.random() * 100;
            const x = centerX + Math.cos(angle) * distance;
            const y = centerY + Math.sin(angle) * distance;
            const radius = 20 + Math.random() * 50;

            const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
            gradient.addColorStop(0, lightColor);
            gradient.addColorStop(0.7, lightColor);
            gradient.addColorStop(1, '#c1440e');

            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(x, y, radius, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    // Add some dust storm variations
    for (let i = 0; i < 30; i++) {
        const x = Math.random() * size;
        const y = Math.random() * size;
        const radius = 5 + Math.random() * 20;

        ctx.fillStyle = '#d2691e';
        ctx.globalAlpha = 0.3;
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1.0;
    }

    // Add polar ice caps (smaller than Earth's)
    const iceColor = '#f5f5f5';
    const polarHeight = size * 0.08;

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
    shininess: 2,
    specular: 0x111111
});

const planet = new THREE.Mesh(geometry, material);
scene.add(planet);

// Add atmosphere glow (thin reddish atmosphere for Mars)
const atmosphereGeometry = new THREE.SphereGeometry(2.08, 64, 64);
const atmosphereMaterial = new THREE.MeshBasicMaterial({
    color: 0xff8844,
    transparent: true,
    opacity: 0.08,
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
const rimLight = new THREE.DirectionalLight(0xffaa88, 0.2);
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

// Animation loop
function animate() {
    requestAnimationFrame(animate);

    // Rotate planet
    planet.rotation.y += 0.002;
    atmosphere.rotation.y += 0.002;

    // Slow rotation of stars for depth
    stars.rotation.y += 0.0001;

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
