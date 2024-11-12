particlesJS('particles-js',
  {
    "particles": {
      "number": {
        "value": 50,
        "density": {
          "enable": true,
          "value_area": 800
        }
      },
      "color": {
        "value": "#60a5fa"
      },
      "shape": {
        "type": "circle"
      },
      "opacity": {
        "value": 0.5,
        "random": false
      },
      "size": {
        "value": 3,
        "random": true
      },
      "line_linked": {
        "enable": true,
        "distance": 150,
        "color": "#60a5fa",
        "opacity": 0.4,
        "width": 1
      },
      "move": {
        "enable": true,
        "speed": 2,
        "direction": "none",
        "random": false,
        "straight": false,
        "out_mode": "out",
        "bounce": false
      }
    },
    "interactivity": {
      "detect_on": "canvas",
      "events": {
        "onhover": {
          "enable": true,
          "mode": "grab"
        },
        "onclick": {
          "enable": true,
          "mode": "push"
        },
        "resize": true
      }
    },
    "retina_detect": true
  }
);

// Close mobile menu when clicking outside
document.addEventListener('click', (e) => {
  if (!e.target.closest('nav')) {
    Alpine.store('showMenu', false);
  }
});

// Add click handlers for course sections
document.querySelectorAll('.course-section').forEach(section => {
  section.addEventListener('click', () => {
    const firstUncompletedLesson = section.querySelector('.lesson-link:not(.opacity-50)');
    if (firstUncompletedLesson && firstUncompletedLesson.href) {
      window.location.href = firstUncompletedLesson.href;
    }
  });
});

// Add hover effects for clickable lessons
document.querySelectorAll('.lesson-link:not(.opacity-50)').forEach(lesson => {
  lesson.addEventListener('mouseenter', () => {
    lesson.classList.add('bg-slate-700/30');
  });
  lesson.addEventListener('mouseleave', () => {
    lesson.classList.remove('bg-slate-700/30');
  });
});