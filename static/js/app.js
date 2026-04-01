// Bangumi-PikPak Web UI 通用脚本

// 工具函数
function formatTimestamp(timestamp) {
    if (!timestamp) return '暂无';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
    
    return date.toLocaleString('zh-CN');
}

function formatUptime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// 页面加载完成后的通用处理
document.addEventListener('DOMContentLoaded', function() {
    // 添加导航栏激活状态
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.fontWeight = 'bold';
            link.style.color = '#4a9eff';
        }
    });
});

// 自动隐藏alert消息
function autoHideAlert() {
    const alerts = document.querySelectorAll('.alert:not(.hidden)');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('hidden');
        }, 5000);
    });
}

// 调用自动隐藏
if (document.readyState === 'complete') {
    autoHideAlert();
} else {
    document.addEventListener('DOMContentLoaded', autoHideAlert);
}