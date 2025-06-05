let currentResumeId = null;

const resumeForm = document.getElementById('resumeForm');
const resumeFile = document.getElementById('resumeFile');
const submitBtn = document.getElementById('submitBtn');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const resumeInfo = document.getElementById('resumeInfo');
const jobMatches = document.getElementById('jobMatches');
const errorMessage = document.getElementById('errorMessage');

const API_BASE = '/api/v1';

document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    setupDragAndDrop();
});

function setupEventListeners() {
    resumeFile.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            document.querySelector('.file-input-wrapper').classList.add('file-selected');
            document.querySelector('.upload-text').textContent = `已选择: ${file.name}`;
        } else {
            document.querySelector('.file-input-wrapper').classList.remove('file-selected');
            document.querySelector('.upload-text').textContent = '点击选择简历文件';
        }
    });

    resumeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        submitResume();
    });
}

async function submitResume() {
    const file = resumeFile.files[0];
    const limit = document.getElementById('matchLimit').value;

    if (!file) {
        showError('请选择一个简历文件');
        return;
    }

    setLoadingState(true);
    hideResults();
    hideError();

    try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('user_id', '1');
        formData.append('limit', limit);

        const response = await fetch(`${API_BASE}/job-matching/submit-resume`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || '处理简历时发生错误');
        }

        currentResumeId = data.resume_info.resume_id;
        displayResults(data);

    } catch (error) {
        console.error('Error submitting resume:', error);
        showError(error.message || '网络错误，请稍后重试');
    } finally {
        setLoadingState(false);
    }
}

function displayResults(data) {
    const resumeInfoHtml = `
        <h3>简历信息</h3>
        <p><strong>文件名:</strong> ${data.resume_info.filename}</p>
        <p><strong>姓名:</strong> ${data.resume_info.parsed_summary.name || '未识别'}</p>
        <p><strong>邮箱:</strong> ${data.resume_info.parsed_summary.email || '未识别'}</p>
        <p><strong>电话:</strong> ${data.resume_info.parsed_summary.phone || '未识别'}</p>
        <p><strong>提取字段数:</strong> ${data.resume_info.parsed_summary.fields_extracted}</p>
    `;
    resumeInfo.innerHTML = resumeInfoHtml;

    const matches = data.job_matches.matches;
    if (matches.length === 0) {
        jobMatches.innerHTML = '<p class="no-matches">未找到匹配的职位</p>';
    } else {
        const matchesHtml = matches.map((match, index) => `
            <div class="job-match-card">
                <div class="match-header">
                    <div>
                        <div class="job-title">${match.job_title}</div>
                        <div class="company-name">${match.company_name}</div>
                    </div>
                    <div class="match-score">${match.match_percentage}</div>
                </div>
                <div class="match-explanation">
                    ${match.explanation}
                </div>
                ${match.details ? `
                    <div class="match-details">
                        <h4>匹配详情</h4>
                        <p>${match.details}</p>
                    </div>
                ` : ''}
            </div>
        `).join('');
        
        jobMatches.innerHTML = matchesHtml;
    }

    showResults();
}

function setLoadingState(loading) {
    const btnText = document.querySelector('.btn-text');
    const loadingSpinner = document.querySelector('.loading-spinner');
    
    if (loading) {
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        loadingSpinner.style.display = 'inline';
    } else {
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        loadingSpinner.style.display = 'none';
    }
}

function showResults() {
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function hideResults() {
    resultsSection.style.display = 'none';
}

function showError(message) {
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
    errorSection.scrollIntoView({ behavior: 'smooth' });
}

function hideError() {
    errorSection.style.display = 'none';
}

function resetForm() {
    resumeForm.reset();
    
    document.querySelector('.file-input-wrapper').classList.remove('file-selected');
    document.querySelector('.upload-text').textContent = '点击选择简历文件';
    
    hideResults();
    hideError();
    
    setLoadingState(false);
    
    currentResumeId = null;
}

function setupDragAndDrop() {
    const fileInputWrapper = document.querySelector('.file-input-wrapper');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileInputWrapper.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        fileInputWrapper.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        fileInputWrapper.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight(e) {
        fileInputWrapper.classList.add('drag-over');
    }
    
    function unhighlight(e) {
        fileInputWrapper.classList.remove('drag-over');
    }
    
    fileInputWrapper.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            resumeFile.files = files;
            resumeFile.dispatchEvent(new Event('change'));
        }
    }
}
