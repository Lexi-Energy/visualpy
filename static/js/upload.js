const SKIP_DIRS = new Set([
    '__pycache__', '.venv', 'venv', 'env', '.git', 'node_modules',
    '__pypackages__', '.tox', '.nox', '.mypy_cache', '.pytest_cache',
    '.eggs', 'dist', 'build', '.idea', '.vscode',
]);

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('folder-input');
const statusEl = document.getElementById('upload-status');
const errorEl = document.getElementById('upload-error');

function showStatus(msg) {
    if (statusEl) statusEl.textContent = msg;
    if (errorEl) errorEl.textContent = '';
    dropZone.classList.add('pointer-events-none', 'opacity-60');
}

function showError(msg) {
    if (errorEl) errorEl.textContent = msg;
    if (statusEl) statusEl.textContent = '';
    dropZone.classList.remove('pointer-events-none', 'opacity-60');
}

function shouldSkip(pathParts) {
    return pathParts.some(function(part) { return SKIP_DIRS.has(part); });
}

function readEntryRecursive(entry) {
    return new Promise(function(resolve) {
        if (entry.isFile) {
            entry.file(function(file) {
                var relPath = entry.fullPath.replace(/^\//, '');
                var parts = relPath.split('/');
                if (file.name.endsWith('.py') && !shouldSkip(parts)) {
                    resolve([{ file: file, path: relPath }]);
                } else {
                    resolve([]);
                }
            }, function(err) {
                console.warn('[visualpy] Could not read file:', entry.fullPath, err);
                resolve([]);
            });
        } else if (entry.isDirectory) {
            var dirParts = entry.fullPath.replace(/^\//, '').split('/');
            if (shouldSkip(dirParts)) { resolve([]); return; }
            var reader = entry.createReader();
            var allEntries = [];
            (function readBatch() {
                reader.readEntries(function(entries) {
                    if (entries.length === 0) {
                        Promise.all(allEntries.map(readEntryRecursive)).then(function(results) {
                            resolve(results.flat());
                        });
                    } else {
                        allEntries = allEntries.concat(Array.from(entries));
                        readBatch();
                    }
                }, function(err) {
                    console.warn('[visualpy] Could not read directory:', entry.fullPath, err);
                    resolve([]);
                });
            })();
        } else {
            resolve([]);
        }
    });
}

function collectFromDataTransfer(dataTransfer) {
    var items = dataTransfer.items;
    var entries = [];
    for (var i = 0; i < items.length; i++) {
        var entry = items[i].webkitGetAsEntry && items[i].webkitGetAsEntry();
        if (entry) entries.push(entry);
    }
    if (entries.length === 0) return Promise.resolve([]);
    return Promise.all(entries.map(readEntryRecursive)).then(function(r) { return r.flat(); });
}

function collectFromInput(files) {
    var result = [];
    for (var i = 0; i < files.length; i++) {
        var file = files[i];
        var relPath = file.webkitRelativePath || file.name;
        var parts = relPath.split('/');
        if (file.name.endsWith('.py') && !shouldSkip(parts)) {
            result.push({ file: file, path: relPath });
        }
    }
    return Promise.resolve(result);
}

function uploadFiles(pyFiles) {
    if (pyFiles.length === 0) {
        showError('No Python files found. Drop a folder containing .py files.');
        return;
    }

    showStatus('Uploading ' + pyFiles.length + ' Python file' + (pyFiles.length === 1 ? '' : 's') + '...');

    var formData = new FormData();
    pyFiles.forEach(function(item) {
        formData.append('files', item.file, item.path);
    });

    fetch('/upload', { method: 'POST', body: formData })
        .then(function(resp) {
            if (resp.status === 429) {
                return resp.json().then(function(data) {
                    showError(data.error || 'Too many requests. Please wait.');
                    return null;
                });
            }
            if (!resp.ok) {
                return resp.json().then(function(data) {
                    showError(data.error || 'Upload failed. Please try again.');
                    return null;
                }).catch(function() {
                    showError('Upload failed (status ' + resp.status + ').');
                    return null;
                });
            }
            return resp.json();
        })
        .then(function(data) {
            if (data && data.success) {
                showStatus('Analysis complete. Loading results...');
                window.location.href = '/';
            }
        })
        .catch(function(err) {
            showError('Connection error: ' + err.message);
        });
}

var dragCounter = 0;

dropZone.addEventListener('dragenter', function(e) {
    e.preventDefault();
    dragCounter++;
    dropZone.classList.add('border-blue-500', 'bg-blue-50', 'dark:bg-blue-900/20');
});

dropZone.addEventListener('dragover', function(e) {
    e.preventDefault();
});

dropZone.addEventListener('dragleave', function(e) {
    e.preventDefault();
    dragCounter--;
    if (dragCounter <= 0) {
        dragCounter = 0;
        dropZone.classList.remove('border-blue-500', 'bg-blue-50', 'dark:bg-blue-900/20');
    }
});

dropZone.addEventListener('drop', function(e) {
    e.preventDefault();
    dragCounter = 0;
    dropZone.classList.remove('border-blue-500', 'bg-blue-50', 'dark:bg-blue-900/20');
    showStatus('Reading files...');
    collectFromDataTransfer(e.dataTransfer).then(uploadFiles).catch(function(err) {
        showError('Could not read dropped files: ' + (err && err.message ? err.message : 'unknown error'));
    });
});

fileInput.addEventListener('change', function() {
    if (fileInput.files.length > 0) {
        showStatus('Reading files...');
        collectFromInput(fileInput.files).then(uploadFiles).catch(function(err) {
            showError('Could not read files: ' + (err && err.message ? err.message : 'unknown error'));
        });
    }
});

document.addEventListener('dragover', function(e) { e.preventDefault(); });
document.addEventListener('drop', function(e) { e.preventDefault(); });
