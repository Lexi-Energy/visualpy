// Mermaid bootstrap, shared by the live server and the static export.
// Expects the Mermaid UMD bundle to have already defined window.mermaid.
(function () {
    'use strict';
    var mermaid = window.mermaid;
    if (!mermaid) { console.error('[visualpy] Mermaid library not loaded'); return; }

    function initMermaid(isDark) {
        mermaid.initialize({
            startOnLoad: false,
            theme: isDark ? 'dark' : 'default',
            securityLevel: 'loose',
            flowchart: { useMaxWidth: true, htmlLabels: true },
        });
    }

    // Store original source BEFORE mermaid.run() replaces it with SVG.
    document.querySelectorAll('.mermaid').forEach(function (el) {
        if (!el.getAttribute('data-mermaid-src')) {
            el.setAttribute('data-mermaid-src', el.textContent.trim());
        }
    });

    initMermaid(document.documentElement.classList.contains('dark'));
    window.mermaidModule = mermaid;

    mermaid.run().catch(function (err) {
        console.error('[visualpy] Mermaid render failed:', err);
        document.querySelectorAll('.mermaid').forEach(function (el) {
            if (!el.querySelector('svg')) {
                el.innerHTML = '<p class="text-sm text-red-600 dark:text-red-400">Diagram failed to render. Check browser console.</p>';
            }
        });
    });

    window.reRenderMermaid = function (isDark) {
        initMermaid(isDark);
        document.querySelectorAll('.mermaid').forEach(function (el) {
            var code = el.getAttribute('data-mermaid-src');
            if (code) {
                el.removeAttribute('data-processed');
                el.innerHTML = code;
            }
        });
        mermaid.run().catch(function (err) {
            console.error('[visualpy] Mermaid re-render failed:', err);
            document.querySelectorAll('.mermaid').forEach(function (el) {
                if (!el.querySelector('svg')) {
                    el.innerHTML = '<p class="text-sm text-red-600 dark:text-red-400">Diagram failed to re-render. Try refreshing the page.</p>';
                }
            });
        });
    };
})();
