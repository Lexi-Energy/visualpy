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
                await window.renderMermaidElement(el, src.textContent.trim());
            }
        }
    }

    // Render mermaid graphs the first time they become visible.
    document.addEventListener('toggle', function (e) {
        if (!e.target.querySelector || !e.target.open) return;
        var el = e.target.querySelector('.mermaid-deferred') || e.target.querySelector('.mermaid');
        if (!el || el.querySelector('svg')) return;
        var src = e.target.querySelector('script[type="text/plain"]');
        if (!src) return;

        function doRender() {
            window.renderMermaidElement(el, src.textContent.trim());
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
                    el.innerHTML = '<p class="text-sm text-gray-400 dark:text-gray-500">Diagram library could not load.</p>';
                }
            }, 5000);
        }
    }, true);

    function initOverviewView() {
        // Render the visible business graph if it's the active view.
        var el = document.querySelector('#graph-biz-container .mermaid-deferred');
        if (el && !el.querySelector('svg')) {
            var src = document.getElementById('graph-biz-collapsed');
            if (src) window.renderMermaidElement(el, src.textContent.trim());
        }
    }

    window.VisualPyOverview = { init: initOverviewView, refreshView: refreshView };
})();