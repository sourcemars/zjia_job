document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('resumeForm');
    const fileInput = document.getElementById('resumeFile');
    const fileWrapper = document.querySelector('.file-input-wrapper');
    const fileText = document.querySelector('.file-text');
    const uploadBtn = document.getElementById('uploadBtn');
    const btnText = document.querySelector('.btn-text');
    const btnLoading = document.querySelector('.btn-loading');
    const resultSection = document.getElementById('result');
    const resultIcon = document.querySelector('.result-icon');
    const resultMessage = document.querySelector('.result-message');
    const resultDetails = document.querySelector('.result-details');

    fileWrapper.addEventListener('dragover', function(e) {
        e.preventDefault();
        fileWrapper.classList.add('dragover');
    });

    fileWrapper.addEventListener('dragleave', function(e) {
        e.preventDefault();
        fileWrapper.classList.remove('dragover');
    });

    fileWrapper.addEventListener('drop', function(e) {
        e.preventDefault();
        fileWrapper.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            updateFileDisplay(files[0]);
        }
    });

    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            updateFileDisplay(e.target.files[0]);
        }
    });

    function updateFileDisplay(file) {
        const fileName = file.name;
        const fileSize = formatFileSize(file.size);
        fileText.textContent = `已选择: ${fileName} (${fileSize})`;
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const file = fileInput.files[0];
        if (!file) {
            showResult('error', '请选择要上传的文件', '');
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            showResult('error', '文件太大', '文件大小不能超过 10MB');
            return;
        }

        const allowedTypes = ['.pdf', '.doc', '.docx', '.txt'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(fileExtension)) {
            showResult('error', '文件类型不支持', `支持的格式: ${allowedTypes.join(', ')}`);
            return;
        }

        setLoading(true);
        hideResult();

        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const userId = document.getElementById('userId').value;
            if (userId) {
                formData.append('user_id', userId);
            }

            const response = await fetch('/api/resumes/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                showResult('success', '上传成功！', 
                    `文件名: ${result.filename}<br>
                     文件大小: ${formatFileSize(result.size)}<br>
                     简历ID: ${result.resume_id}`);
                form.reset();
                fileText.textContent = '点击选择文件或拖拽文件到此处';
            } else {
                showResult('error', '上传失败', result.detail || '未知错误');
            }
        } catch (error) {
            console.error('Upload error:', error);
            showResult('error', '上传失败', '网络错误，请检查连接后重试');
        } finally {
            setLoading(false);
        }
    });

    function setLoading(loading) {
        uploadBtn.disabled = loading;
        if (loading) {
            btnText.style.display = 'none';
            btnLoading.style.display = 'block';
        } else {
            btnText.style.display = 'block';
            btnLoading.style.display = 'none';
        }
    }

    function showResult(type, message, details) {
        resultSection.className = `result-section ${type}`;
        resultIcon.textContent = type === 'success' ? '✅' : '❌';
        resultMessage.textContent = message;
        resultDetails.innerHTML = details;
        resultSection.style.display = 'block';
        
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function hideResult() {
        resultSection.style.display = 'none';
    }
});
