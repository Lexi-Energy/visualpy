(function () {
    'use strict';
    document.addEventListener('keydown', function (e) {
        if (window.getViewMode() !== 'presentation') return;

        if (e.key === 'Escape') {
            localStorage.setItem('viewMode', 'business');
            window.location.reload();
            return;
        }

        var phases = document.querySelectorAll('#script-view-root > div:first-child details');
        if (!phases.length) return;
        var openIdx = Array.from(phases).findIndex(function (d) { return d.open; });
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
            phases.forEach(function (d) { d.removeAttribute('open'); });
            var next = phases[Math.min(openIdx + 1, phases.length - 1)];
            next.setAttribute('open', '');
            next.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
            phases.forEach(function (d) { d.removeAttribute('open'); });
            var prev = phases[Math.max(openIdx - 1, 0)];
            prev.setAttribute('open', '');
            prev.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
})();