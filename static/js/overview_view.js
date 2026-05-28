// Interactive behaviour for the project overview. Shared by the live server
// (overview.html) and the self-contained export.
(function () {
    'use strict';

    async function refreshView(isBiz) {
        if (!window.mermaidModule) {
            console.warn('[visualpy] View toggled before Mermaid loaded');
            return;
        }
        if (!isBiz) {
            var src = document.getElementById('graph-tech');
            var el = document.querySelector('#tech-graph-container .mermaid');
            if (src && el) {
                if (el.dataset.rendering === '1') return;  // guard against concurrent run() on rapid toggle
                el.dataset.rendering = '1';
                var code = src.textContent.trim();
                el.setAttribute('data-mermaid-src', code);
                el.removeAttribute('data-processed');
                el.innerHTML = code;
                try { await window.mermaidModule.run({ nodes: [el] }); }
                catch (err) {
                    console.error('[visualpy] Mermaid re-render failed:', err);
                    el.innerHTML = '<p class="text-sm text-red-600 dark:text-red-400">Diagram failed to render. Try refreshing the page.</p>';
                }
                finally { delete el.dataset.rendering; }
            }
        }
    }

    // Render collapsed mermaid graphs the first time their <details> opens.
    document.addEventListener('toggle', function (e) {
        if (!e.target.querySelector || !e.target.open) return;
        var el = e.target.querySelector('.mermaid-deferred') || e.target.querySelector('.mermaid');
        if (!el || el.querySelector('svg')) return;
        var src = e.target.querySelector('script[type="text/plain"]');
        if (!src) return;

        function doRender() {
            if (el.dataset.rendering === '1') return;  // a second toggle listener may also fire
            el.dataset.rendering = '1';
            var code = src.textContent.trim();
            el.className = 'mermaid';
            el.setAttribute('data-mermaid-src', code);
            el.removeAttribute('data-processed');
            el.innerHTML = code;
            window.mermaidModule.run({ nodes: [el] }).catch(function (err) {
                console.error('[visualpy] Mermaid render failed:', err);
                el.innerHTML = '<p class="text-sm text-red-600 dark:text-red-400">Diagram failed to render. Try refreshing the page.</p>';
            }).finally(function () { delete el.dataset.rendering; });
        }

        if (window.mermaidModule) {
            doRender();
        } else {
            el.innerHTML = '<p class="text-sm text-gray-400 dark:text-gray-500">Loading diagram...</p>';
            var retry = setInterval(function () {
                if (window.mermaidModule) { clearInterval(retry); doRender(); }
            }, 100);
            setTimeout(function () {
                clearInterval(retry);
                if (!el.querySelector('svg')) {
                    el.innerHTML = '<p class="text-sm text-gray-400 dark:text-gray-500">Diagram library could not load. Check your connection and refresh.</p>';
                }
            }, 5000);
        }
    }, true);

    function initOverviewView() {
        // The visible technical graph is rendered by the page's Mermaid bootstrap;
        // collapsed/business graphs render lazily via the toggle listener above.
    }

    window.VisualPyOverview = { init: initOverviewView, refreshView: refreshView };
})();
