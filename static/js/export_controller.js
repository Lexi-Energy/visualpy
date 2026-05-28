// Same-document navigation for the self-contained export. One script body is
// shown at a time in #view-script; the overview lives in #view-overview.
(function () {
    'use strict';

    var _bodiesEl = document.getElementById('script-bodies');
    try {
        window.SCRIPT_BODIES = JSON.parse((_bodiesEl && _bodiesEl.textContent) || '{}');
    } catch (err) {
        console.error('[visualpy] Could not parse script bodies:', err);
        window.SCRIPT_BODIES = {};
    }

    function _overview() { return document.getElementById('view-overview'); }
    function _scriptView() { return document.getElementById('view-script'); }

    window.showScript = function (path) {
        var container = _scriptView();
        if (!container) return;
        var body = window.SCRIPT_BODIES[path];
        if (!body) {
            container.innerHTML = '<p class="text-sm text-red-600 dark:text-red-400">Could not load this script’s view.</p>';
            container.hidden = false;
            var ovMissing = _overview();
            if (ovMissing) ovMissing.hidden = true;
            return;
        }
        container.innerHTML = body;
        container.hidden = false;
        var ov = _overview();
        if (ov) ov.hidden = true;
        window.scrollTo(0, 0);
        // Defer a frame so Alpine binds the injected x-show nodes before we render
        // diagrams — avoids a flash where both view modes are briefly visible.
        requestAnimationFrame(function () {
            if (window.VisualPyScript) window.VisualPyScript.init();
        });
    };

    window.showOverview = function () {
        var container = _scriptView();
        if (container) { container.hidden = true; container.innerHTML = ''; }
        var ov = _overview();
        if (ov) ov.hidden = false;
        window.scrollTo(0, 0);
        if (window.VisualPyOverview) window.VisualPyOverview.init();
    };

    window.switchViewMode = function (isBiz) {
        var sv = _scriptView();
        if (sv && !sv.hidden && window.VisualPyScript) return window.VisualPyScript.refreshView(isBiz);
        if (window.VisualPyOverview) return window.VisualPyOverview.refreshView(isBiz);
    };

    document.addEventListener('DOMContentLoaded', function () {
        if (window.VisualPyOverview) window.VisualPyOverview.init();
    });
})();
