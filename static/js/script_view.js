// Interactive behaviour for a single script view. Shared by the live server
// (script.html) and the self-contained export, where one script body is shown
// at a time in a single container — so the fixed element IDs never collide.
(function () {
    'use strict';

    window.STEP_DETAILS = window.STEP_DETAILS || {};
    var _openStepKey = null;
    var _flowIsCompact = false;
    var _flowIsBusiness = window.isBusinessView();

    function _injectStepDetail() {
        if (!_openStepKey) return;
        var entry = window.STEP_DETAILS[_openStepKey];
        if (!entry) return;
        var isBiz = window.isBusinessView();
        var content = document.getElementById(isBiz ? 'step-detail-content-biz' : 'step-detail-content')
            || document.getElementById('step-detail-content-biz')
            || document.getElementById('step-detail-content');
        if (content) content.innerHTML = isBiz ? entry.business : entry.technical;
    }

    window.showStepDetail = function (scriptPath, line) {
        _openStepKey = scriptPath + '::' + line;
        var isBiz = window.isBusinessView();
        var panelId = isBiz ? 'step-detail-biz' : 'step-detail';
        var content = document.getElementById(isBiz ? 'step-detail-content-biz' : 'step-detail-content');
        if (!content) {
            content = document.getElementById('step-detail-content-biz') || document.getElementById('step-detail-content');
            panelId = content ? content.parentElement.id : null;
        }
        if (!content) { console.warn('[visualpy] No step detail panel found'); return; }
        var entry = window.STEP_DETAILS[_openStepKey];
        if (!entry) {
            content.innerHTML = '<p class="text-sm text-red-600 dark:text-red-400">Step details unavailable.</p>';
            return;
        }
        content.innerHTML = isBiz ? entry.business : entry.technical;
        if (panelId) document.getElementById(panelId).scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    };

    function _getFlowSourceId() {
        var scale = _flowIsCompact ? 'compact' : 'detailed';
        return _flowIsBusiness ? 'flow-' + scale + '-biz' : 'flow-' + scale;
    }

    async function _renderMermaidElement(el, code) {
        await window.renderMermaidElement(el, code);
    }

    async function _renderCurrentFlow() {
        var src = document.getElementById(_getFlowSourceId());
        var el = document.getElementById('mermaid-tech');
        if (src && el) await _renderMermaidElement(el, src.textContent.trim());
    }

    async function _renderPedagogical() {
        var src = document.getElementById('flow-pedagogical');
        var el = document.getElementById('mermaid-pedagogical');
        if (src && el) await _renderMermaidElement(el, src.textContent.trim());
    }

    window.switchFlow = async function () {
        _flowIsCompact = !_flowIsCompact;
        var btn = document.getElementById('flow-toggle');
        if (btn) btn.textContent = _flowIsCompact ? 'Show Detailed' : 'Show Compact';
        await _renderCurrentFlow();
    };

    async function refreshView(isBiz) {
        _flowIsBusiness = isBiz;
        _injectStepDetail();
        if (isBiz) {
            await _renderPedagogical();
        } else {
            await _renderCurrentFlow();
        }
    }

    // Collapsed technical diagram renders the first time its <details> opens.
    document.addEventListener('toggle', function (e) {
        if (e.target.querySelector && e.target.open) {
            var el = e.target.querySelector('#mermaid-tech-collapsed') || e.target.querySelector('.mermaid-deferred');
            if (el && !el.querySelector('svg')) {
                var src = document.getElementById('flow-tech-collapsed');
                if (src) window.renderMermaidElement(el, src.textContent.trim()).catch(function (err) {
                    console.error('[visualpy] Collapsed tech diagram render failed:', err);
                });
            }
        }
    }, true);

    // (Re)initialise rendering for the script body currently in the DOM.
    function initScriptView() {
        _openStepKey = null;
        _flowIsBusiness = window.isBusinessView();
        var root = document.getElementById('script-view-root');
        _flowIsCompact = !!(root && root.dataset.defaultCompact === 'true');
        var btn = document.getElementById('flow-toggle');
        if (btn) btn.textContent = _flowIsCompact ? 'Show Detailed' : 'Show Compact';

        var check = setInterval(function () {
            if (window.mermaidModule) {
                clearInterval(check);
                if (_flowIsBusiness) { _renderPedagogical(); } else { _renderCurrentFlow(); }
            }
        }, 50);
        setTimeout(function () {
            clearInterval(check);
            if (!window.mermaidModule) {
                document.querySelectorAll('.mermaid, .mermaid-deferred').forEach(function (el) {
                    if (!el.querySelector('svg')) {
                        el.innerHTML = '<p class="text-sm text-gray-400 dark:text-gray-500">Diagram library could not load. Check your connection and refresh.</p>';
                    }
                });
            }
        }, 5000);
    }

    window.VisualPyScript = { init: initScriptView, refreshView: refreshView };
})();