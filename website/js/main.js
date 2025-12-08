document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Scroll Reveal Animation
    const reveals = document.querySelectorAll('.reveal');

    const revealOnScroll = () => {
        const windowHeight = window.innerHeight;
        const elementVisible = 100;

        reveals.forEach((reveal) => {
            const elementTop = reveal.getBoundingClientRect().top;
            if (elementTop < windowHeight - elementVisible) {
                reveal.classList.add('active');
            }
        });
    };

    window.addEventListener('scroll', revealOnScroll);
    // Trigger once on load
    revealOnScroll();

    // 2. Lightbox Functionality
    // Create Lightbox Elements
    const lightboxOverlay = document.createElement('div');
    lightboxOverlay.className = 'lightbox-overlay';
    
    const lightboxImg = document.createElement('img');
    lightboxImg.className = 'lightbox-img';
    
    const closeBtn = document.createElement('div');
    closeBtn.className = 'lightbox-close';
    closeBtn.innerHTML = '&times;';
    
    lightboxOverlay.appendChild(lightboxImg);
    lightboxOverlay.appendChild(closeBtn);
    document.body.appendChild(lightboxOverlay);

    // Add click event to all images inside academic-container
    const images = document.querySelectorAll('.academic-container img');
    images.forEach(img => {
        // Add hover class if not present
        img.classList.add('hover-scale');
        
        img.addEventListener('click', () => {
            lightboxImg.src = img.src;
            lightboxOverlay.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevent scrolling
        });
    });

    // Close Lightbox
    const closeLightbox = () => {
        lightboxOverlay.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
    };

    closeBtn.addEventListener('click', closeLightbox);
    lightboxOverlay.addEventListener('click', (e) => {
        if (e.target === lightboxOverlay) {
            closeLightbox();
        }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && lightboxOverlay.classList.contains('active')) {
            closeLightbox();
        }
    });

    // 3. Particle Network Animation (Canvas)
    const canvas = document.getElementById('particle-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let width, height;
        let particles = [];

        // Configuration
        const particleCount = 80; // Increased count
        const connectionDistance = 180; // Increased distance
        const mouseDistance = 250;

        // Resize handling
        const resize = () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        };
        window.addEventListener('resize', resize);
        resize();

        // Mouse tracking
        let mouse = { x: null, y: null };
        window.addEventListener('mousemove', (e) => {
            mouse.x = e.x;
            mouse.y = e.y;
        });
        window.addEventListener('mouseout', () => {
            mouse.x = null;
            mouse.y = null;
        });

        // Particle Class
        class Particle {
            constructor() {
                this.x = Math.random() * width;
                this.y = Math.random() * height;
                // Base velocity for wandering
                this.baseVx = (Math.random() - 0.5) * 0.5; 
                this.baseVy = (Math.random() - 0.5) * 0.5;
                // Current velocity
                this.vx = this.baseVx;
                this.vy = this.baseVy;
                
                this.size = Math.random() * 3 + 2; 
                this.color = `rgba(203, 213, 225, ${Math.random() * 0.5 + 0.3})`; 
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;

                // Bounce off edges
                if (this.x < 0 || this.x > width) {
                    this.vx *= -1;
                    this.baseVx *= -1; // Also reflect base velocity
                }
                if (this.y < 0 || this.y > height) {
                    this.vy *= -1;
                    this.baseVy *= -1;
                }

                // Mouse interaction
                if (mouse.x != null) {
                    let dx = mouse.x - this.x;
                    let dy = mouse.y - this.y;
                    let distance = Math.sqrt(dx * dx + dy * dy);
                    if (distance < mouseDistance) {
                        const forceDirectionX = dx / distance;
                        const forceDirectionY = dy / distance;
                        const force = (mouseDistance - distance) / mouseDistance;
                        // Reduced force multiplier significantly (0.6 -> 0.05)
                        const directionX = forceDirectionX * force * 0.05;
                        const directionY = forceDirectionY * force * 0.05;
                        
                        // Push away (repulsion) instead of attraction for better feel? 
                        // Or keep attraction but weaker. Let's keep attraction but weaker.
                        this.vx -= directionX; // Changed to repulsion (-) to push particles away from mouse
                        this.vy -= directionY;
                    }
                }

                // Friction / Return to base velocity
                // Smoothly interpolate current velocity back to base velocity
                this.vx += (this.baseVx - this.vx) * 0.05;
                this.vy += (this.baseVy - this.vy) * 0.05;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
            }
        }

        // Initialize particles
        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle());
        }

        // Animation Loop
        const animate = () => {
            ctx.clearRect(0, 0, width, height);
            
            for (let i = 0; i < particles.length; i++) {
                particles[i].update();
                particles[i].draw();

                // Draw connections
                for (let j = i; j < particles.length; j++) {
                    let dx = particles[i].x - particles[j].x;
                    let dy = particles[i].y - particles[j].y;
                    let distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < connectionDistance) {
                        ctx.beginPath();
                        // Brighter lines
                        ctx.strokeStyle = `rgba(203, 213, 225, ${1 - distance / connectionDistance})`;
                        ctx.lineWidth = 1.5; // Thicker lines
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.stroke();
                    }
                }
            }
            requestAnimationFrame(animate);
        };
        animate();
    }
});
